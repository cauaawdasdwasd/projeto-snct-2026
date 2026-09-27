# Vídeos dos protocolos

Os seis tutoriais são animações desenhadas por código (`src/rendering/protocol_films.py`)
e tocam direto no popup de cada protocolo, sem depender de codec de vídeo.

Os mesmos filmes foram exportados para MP4 (15 s, 1080x570) para uso em slides e
apresentações:

- `grace_hopper.mp4`, `katherine_johnson.mp4`, `ada_lovelace.mp4`
- `radia_perlman.mp4`, `fei_fei_li.mp4`, `margaret_hamilton.mp4`

Para regenerar depois de mudar uma animação (precisa do `ffmpeg` instalado):

```powershell
python scripts/render_protocol_videos.py            # todos
python scripts/render_protocol_videos.py fei_fei_li # só um
```

Os MP4 não têm áudio; dentro do jogo o filme toca sons de interface nos momentos-chave.
