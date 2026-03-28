# VideoDownloader

Baixe vídeos do YouTube, Instagram e Twitter/X com interface gráfica.

---

## Aviso Legal

Este projeto é apenas para fins educacionais.  
O download de conteúdo protegido por direitos autorais pode violar os Termos de Uso das plataformas e legislações locais.  
**Use somente com conteúdos que você tem permissão para baixar. Use com responsabilidade.**

---

## Download

Acesse a seção **[Releases](../../releases)** e baixe o `VideoDownloader.exe`.  
Não é necessário instalar Python, bibliotecas ou qualquer outro programa.

---

## Funcionalidades

- Baixar vídeos do YouTube, Instagram e Twitter/X
- Escolher entre **vídeo completo** ou **apenas áudio**
- Selecionar qualidade: Melhor, 1080p, 720p ou 360p
- Selecionar formato de áudio: MP3, M4A ou WAV
- Escolher a pasta de destino do download
- Barra de progresso em tempo real com velocidade e tempo estimado

---

## Como usar

1. Baixe o `VideoDownloader.exe` na seção de Releases
2. Execute o arquivo — nenhuma instalação necessária
3. Cole a URL do vídeo desejado
4. Escolha o tipo de download e a qualidade
5. Clique em **Baixar agora**

---

## Plataformas suportadas

| Plataforma  | Vídeo | Áudio |
|-------------|-------|-------|
| YouTube     | ✅    | ✅    |
| Instagram   | ✅    | ✅    |
| Twitter/X   | ✅    | ✅    |

---

## Para desenvolvedores

Se quiser rodar ou modificar o projeto localmente:

### Requisitos

- Python 3.x
- [ffmpeg.exe](https://www.gyan.dev/ffmpeg/builds/) na mesma pasta que o `main.py`

### Instalação

```bash
git clone https://github.com/gcanedop/videodownloader.git
cd videodownloader
pip install -r requirements.txt
python main.py
```

### Gerar o executável

Com o `ffmpeg.exe` na pasta do projeto, execute:

```bash
build.bat
```

O `.exe` será gerado em `dist/VideoDownloader.exe`.

---

## Tecnologias utilizadas

- [Python](https://python.org)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org)
- [PyInstaller](https://pyinstaller.org)
