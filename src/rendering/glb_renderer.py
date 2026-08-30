from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import moderngl
import numpy as np
import pygame
import trimesh


VERTEX_SHADER = """
#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

uniform mat4 mvp;
uniform mat4 model;

out vec3 normal;
out vec2 uv;

void main() {
    gl_Position = mvp * vec4(in_position, 1.0);
    normal = normalize(mat3(model) * in_normal);
    uv = vec2(in_uv.x, 1.0 - in_uv.y);
}
"""


FRAGMENT_SHADER = """
#version 330

uniform sampler2D base_color;

in vec3 normal;
in vec2 uv;

out vec4 color;

void main() {
    vec4 albedo = texture(base_color, uv);
    if (albedo.a < 0.02) {
        discard;
    }

    vec3 light_direction = normalize(vec3(-0.35, 0.55, 0.78));
    float diffuse = abs(dot(normalize(normal), light_direction));
    float lighting = 0.78 + diffuse * 0.22;
    color = vec4(albedo.rgb * lighting, albedo.a);
}
"""


@dataclass
class _MeshPart:
    vertex_array: moderngl.VertexArray
    vertex_buffer: moderngl.Buffer
    index_buffer: moderngl.Buffer
    texture: moderngl.Texture
    index_count: int

    def release(self) -> None:
        self.vertex_array.release()
        self.vertex_buffer.release()
        self.index_buffer.release()
        self.texture.release()


class GlbRenderer:
    """Render a textured GLB into a transparent Pygame surface."""

    def __init__(
        self,
        model_path: Path,
        render_size: tuple[int, int] = (1280, 720),
    ) -> None:
        self.render_size = render_size
        self.context = moderngl.create_standalone_context(require=330)
        self.program = self.context.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER,
        )
        self.color_texture = self.context.texture(render_size, components=4)
        self.depth_buffer = self.context.depth_renderbuffer(render_size)
        self.framebuffer = self.context.framebuffer(
            color_attachments=(self.color_texture,),
            depth_attachment=self.depth_buffer,
        )
        self.parts: list[_MeshPart] = []
        self.model_center = np.zeros(3, dtype=np.float32)
        self.model_scale = 1.0
        self._load_model(model_path)

    def render(
        self,
        rotation_x: float,
        rotation_y: float,
        zoom: float,
    ) -> pygame.Surface:
        self.framebuffer.use()
        self.context.viewport = (0, 0, *self.render_size)
        self.context.enable(moderngl.DEPTH_TEST | moderngl.BLEND)
        self.context.disable(moderngl.CULL_FACE)
        self.context.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
        )
        self.framebuffer.clear(0.0, 0.0, 0.0, 0.0, depth=1.0)

        center = self._translation_matrix(-self.model_center)
        normalized = self._scale_matrix(self.model_scale * zoom)
        # The exported post-it lies on XZ. Rotate it once so its front faces camera.
        base_orientation = self._rotation_x(np.pi / 2.0)
        user_rotation = self._rotation_y(rotation_y) @ self._rotation_x(rotation_x)
        model = user_rotation @ base_orientation @ normalized @ center

        width, height = self.render_size
        projection = self._perspective_matrix(38.0, width / height, 0.1, 100.0)
        view = self._translation_matrix(np.array((0.0, 0.0, -4.0), dtype=np.float32))
        mvp = projection @ view @ model
        self.program["model"].write(self._matrix_bytes(model))
        self.program["mvp"].write(self._matrix_bytes(mvp))
        self.program["base_color"].value = 0

        for part in self.parts:
            part.texture.use(location=0)
            part.vertex_array.render(
                mode=moderngl.TRIANGLES,
                vertices=part.index_count,
            )

        pixels = self.framebuffer.read(components=4, alignment=1)
        rendered = pygame.image.frombuffer(pixels, self.render_size, "RGBA")
        return pygame.transform.flip(rendered, False, True).copy()

    def release(self) -> None:
        for part in self.parts:
            part.release()
        self.parts.clear()
        self.framebuffer.release()
        self.depth_buffer.release()
        self.color_texture.release()
        self.program.release()
        self.context.release()

    def _load_model(self, model_path: Path) -> None:
        scene = trimesh.load(model_path, force="scene", process=False)
        if not isinstance(scene, trimesh.Scene) or not scene.geometry:
            raise ValueError(f"GLB has no renderable geometry: {model_path}")

        all_vertices: list[np.ndarray] = []
        mesh_data: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, object]] = []
        for node_name in scene.graph.nodes_geometry:
            transform, geometry_name = scene.graph[node_name]
            geometry = scene.geometry[geometry_name]
            if not isinstance(geometry, trimesh.Trimesh) or len(geometry.faces) == 0:
                continue

            vertices = trimesh.transform_points(geometry.vertices, transform).astype(np.float32)
            normal_matrix = np.linalg.inv(transform[:3, :3]).T
            normals = (geometry.vertex_normals @ normal_matrix.T).astype(np.float32)
            normal_lengths = np.linalg.norm(normals, axis=1, keepdims=True)
            normals /= np.maximum(normal_lengths, 1e-7)
            uv = getattr(geometry.visual, "uv", None)
            if uv is None or len(uv) != len(vertices):
                uv = np.zeros((len(vertices), 2), dtype=np.float32)
            else:
                uv = np.asarray(uv, dtype=np.float32)
            indices = np.asarray(geometry.faces, dtype=np.uint32).reshape(-1)
            material = getattr(geometry.visual, "material", None)
            mesh_data.append((vertices, normals, uv, indices, material))
            all_vertices.append(vertices)

        if not mesh_data:
            raise ValueError(f"GLB has no triangle meshes: {model_path}")

        bounds_vertices = np.concatenate(all_vertices, axis=0)
        minimum = bounds_vertices.min(axis=0)
        maximum = bounds_vertices.max(axis=0)
        self.model_center = ((minimum + maximum) * 0.5).astype(np.float32)
        largest_extent = float(np.max(maximum - minimum))
        if largest_extent <= 0.0:
            raise ValueError(f"GLB geometry has invalid dimensions: {model_path}")
        self.model_scale = 2.2 / largest_extent

        for vertices, normals, uv, indices, material in mesh_data:
            interleaved = np.concatenate((vertices, normals, uv), axis=1).astype(np.float32)
            vertex_buffer = self.context.buffer(interleaved.tobytes())
            index_buffer = self.context.buffer(indices.tobytes())
            texture = self._create_texture(material)
            vertex_array = self.context.vertex_array(
                self.program,
                [(vertex_buffer, "3f 3f 2f", "in_position", "in_normal", "in_uv")],
                index_buffer,
                index_element_size=4,
            )
            self.parts.append(
                _MeshPart(
                    vertex_array,
                    vertex_buffer,
                    index_buffer,
                    texture,
                    len(indices),
                )
            )

    def _create_texture(self, material: object) -> moderngl.Texture:
        image = getattr(material, "baseColorTexture", None)
        if image is None:
            texture = self.context.texture((1, 1), 4, bytes((220, 185, 130, 255)))
        else:
            image = image.convert("RGBA")
            texture = self.context.texture(image.size, 4, image.tobytes())
        texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        texture.repeat_x = False
        texture.repeat_y = False
        texture.build_mipmaps()
        try:
            texture.anisotropy = min(8.0, self.context.max_anisotropy)
        except (AttributeError, moderngl.Error):
            pass
        return texture

    @staticmethod
    def _matrix_bytes(matrix: np.ndarray) -> bytes:
        return np.asarray(matrix, dtype=np.float32).T.tobytes()

    @staticmethod
    def _translation_matrix(offset: np.ndarray) -> np.ndarray:
        matrix = np.identity(4, dtype=np.float32)
        matrix[:3, 3] = offset[:3]
        return matrix

    @staticmethod
    def _scale_matrix(scale: float) -> np.ndarray:
        matrix = np.identity(4, dtype=np.float32)
        matrix[0, 0] = scale
        matrix[1, 1] = scale
        matrix[2, 2] = scale
        return matrix

    @staticmethod
    def _rotation_x(angle: float) -> np.ndarray:
        cosine = np.cos(angle)
        sine = np.sin(angle)
        return np.array(
            (
                (1.0, 0.0, 0.0, 0.0),
                (0.0, cosine, -sine, 0.0),
                (0.0, sine, cosine, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
            dtype=np.float32,
        )

    @staticmethod
    def _rotation_y(angle: float) -> np.ndarray:
        cosine = np.cos(angle)
        sine = np.sin(angle)
        return np.array(
            (
                (cosine, 0.0, sine, 0.0),
                (0.0, 1.0, 0.0, 0.0),
                (-sine, 0.0, cosine, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
            dtype=np.float32,
        )

    @staticmethod
    def _perspective_matrix(
        field_of_view: float,
        aspect: float,
        near: float,
        far: float,
    ) -> np.ndarray:
        focal = 1.0 / np.tan(np.radians(field_of_view) * 0.5)
        matrix = np.zeros((4, 4), dtype=np.float32)
        matrix[0, 0] = focal / aspect
        matrix[1, 1] = focal
        matrix[2, 2] = (far + near) / (near - far)
        matrix[2, 3] = (2.0 * far * near) / (near - far)
        matrix[3, 2] = -1.0
        return matrix
