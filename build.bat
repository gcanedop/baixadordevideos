@echo off
echo ============================================
echo  VideoDownloader - Gerando .exe
echo ============================================
echo.

REM 1. Instala dependencias
echo [1/3] Instalando dependencias...
pip install customtkinter yt-dlp pyinstaller --quiet

REM 2. Baixa o ffmpeg.exe (coloque manualmente na mesma pasta se preferir)
echo.
echo [2/3] Verificando ffmpeg...
if not exist ffmpeg.exe (
    echo ATENCAO: ffmpeg.exe nao encontrado nesta pasta.
    echo Baixe em https://www.gyan.dev/ffmpeg/builds/
    echo Copie o ffmpeg.exe para esta pasta e rode o build novamente.
    pause
    exit /b 1
)

REM 3. Gera o .exe
echo.
echo [3/3] Gerando .exe com PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "VideoDownloader" ^
    --add-binary "ffmpeg.exe;." ^
    main.py

echo.
echo ============================================
echo  Pronto! O arquivo esta em: dist\VideoDownloader.exe
echo ============================================
pause
