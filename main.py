import customtkinter as ctk
import yt_dlp
import threading
import os
import sys
from tkinter import filedialog, messagebox

# ── Tema ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ── Utilitário: caminho do FFmpeg embutido pelo PyInstaller ───────────────────
def get_ffmpeg_path():
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    ffmpeg = os.path.join(base, "ffmpeg.exe")
    return ffmpeg if os.path.exists(ffmpeg) else None


# Janela principal 
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VideoDownloader")
        self.geometry("560x660")
        self.resizable(False, False)
        self.configure(fg_color="#0f0f1a")

        self._download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self._is_downloading = False

        self._build_ui()
        self._check_ffmpeg()

    # Verifica FFmpeg ao iniciar 
    def _check_ffmpeg(self):
        if get_ffmpeg_path() is None:
            self._set_status("ffmpeg.exe não encontrado. (downloads sem áudio podem ocorrer)")

    # UI 
    def _build_ui(self):
        PAD = 24

        # Cabeçalho — inner frame empilha os dois labels sem sobreposição
        header = ctk.CTkFrame(self, fg_color="#18182e", corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.place(relx=0, rely=0.5, anchor="w", x=PAD)

        ctk.CTkLabel(
            inner,
            text="⬇  VideoDownloader",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#c4b5fd",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text="YouTube · Instagram · Twitter/X e mais",
            font=ctk.CTkFont(size=11),
            text_color="#555577",
            anchor="w",
        ).pack(anchor="w")

        # Corpo
        body = ctk.CTkScrollableFrame(self, fg_color="#0f0f1a", corner_radius=0)
        body.pack(fill="both", expand=True, padx=PAD, pady=(PAD, 0))

        # URL
        self._section_label(body, "URL DO VÍDEO")
        url_row = ctk.CTkFrame(body, fg_color="transparent")
        url_row.pack(fill="x", pady=(6, 18))

        self.url_entry = ctk.CTkEntry(
            url_row,
            placeholder_text="https://www.youtube.com/watch?v=...",
            fg_color="#12122a",
            border_color="#333355",
            text_color="#c4b5fd",
            placeholder_text_color="#44446a",
            height=42,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            url_row,
            text="Colar",
            width=70,
            height=42,
            fg_color="#2d2b55",
            hover_color="#3d3b75",
            text_color="#a5b4fc",
            border_color="#4f46e5",
            border_width=1,
            command=self._paste_url,
        ).pack(side="left")

        # Tipo de download
        self._section_label(body, "TIPO DE DOWNLOAD")
        tab_row = ctk.CTkFrame(body, fg_color="transparent")
        tab_row.pack(fill="x", pady=(6, 18))

        self.download_type = ctk.StringVar(value="video")

        self.btn_video = ctk.CTkButton(
            tab_row, text="🎬  Vídeo completo", height=48,
            fg_color="#2d2b55", hover_color="#3d3b75",
            text_color="#c4b5fd", border_color="#7c3aed", border_width=1,
            command=lambda: self._select_type("video"),
        )
        self.btn_video.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_audio = ctk.CTkButton(
            tab_row, text="🎵  Apenas áudio", height=48,
            fg_color="#12122a", hover_color="#1e1e3a",
            text_color="#666688", border_color="#333355", border_width=1,
            command=lambda: self._select_type("audio"),
        )
        self.btn_audio.pack(side="left", fill="x", expand=True)

        # Qualidade do vídeo
        self.quality_label = self._section_label(body, "QUALIDADE DO VÍDEO")

        self.quality_var = ctk.StringVar(value="best")
        self.quality_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.quality_frame.pack(fill="x", pady=(6, 18))

        # Formatos com fallback robusto que sempre garante áudio
        qualities = [
            ("Melhor", "best"),
            ("1080p",  "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"),
            ("720p",   "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"),
            ("360p",   "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]"),
        ]
        self.quality_buttons = []
        for label, value in qualities:
            is_first = value == "best"
            btn = ctk.CTkButton(
                self.quality_frame,
                text=label, height=38, width=0,
                fg_color="#2d2b55" if is_first else "#12122a",
                hover_color="#2d2b55",
                text_color="#c4b5fd" if is_first else "#666688",
                border_color="#7c3aed" if is_first else "#333355",
                border_width=1,
                command=lambda v=value: self._select_quality(v),
            )
            btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
            self.quality_buttons.append((btn, value))

        # Formato de áudio (oculto inicialmente)
        self.audio_label = self._section_label(body, "FORMATO DE ÁUDIO")
        self.audio_label.pack_forget()

        self.audio_var = ctk.StringVar(value="mp3")
        self.audio_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.audio_buttons = []

        for fmt in ["MP3", "M4A", "WAV"]:
            is_first = fmt == "MP3"
            btn = ctk.CTkButton(
                self.audio_frame,
                text=fmt, height=38, width=0,
                fg_color="#2d2b55" if is_first else "#12122a",
                hover_color="#2d2b55",
                text_color="#c4b5fd" if is_first else "#666688",
                border_color="#7c3aed" if is_first else "#333355",
                border_width=1,
                command=lambda f=fmt.lower(): self._select_audio_fmt(f),
            )
            btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
            self.audio_buttons.append((btn, fmt.lower()))

        # Pasta de destino
        self._section_label(body, "PASTA DE DESTINO")
        dest_row = ctk.CTkFrame(body, fg_color="transparent")
        dest_row.pack(fill="x", pady=(6, 18))

        self.dest_label = ctk.CTkLabel(
            dest_row,
            text=self._shorten_path(self._download_folder),
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#666688",
            anchor="w",
        )
        self.dest_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            dest_row,
            text="Procurar...",
            width=100, height=36,
            fg_color="#12122a", hover_color="#1e1e3a",
            text_color="#888899", border_color="#333355", border_width=1,
            command=self._choose_folder,
        ).pack(side="left", padx=(8, 0))

        # Botão de download
        self.download_btn = ctk.CTkButton(
            body,
            text="⬇   Baixar agora",
            height=52,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            text_color="white",
            corner_radius=12,
            command=self._start_download,
        )
        self.download_btn.pack(fill="x", pady=(4, 18))

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(
            body, height=6,
            fg_color="#12122a",
            progress_color="#7c3aed",
            corner_radius=3,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            body,
            text="Aguardando...",
            font=ctk.CTkFont(size=12),
            text_color="#555577",
            anchor="w",
        )
        self.status_label.pack(fill="x", pady=(0, PAD))

    # Helpers de UI 
    def _section_label(self, parent, text):
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#555577",
            anchor="w",
        )
        lbl.pack(fill="x")
        return lbl

    def _shorten_path(self, path, maxlen=52):
        return path if len(path) <= maxlen else "..." + path[-(maxlen - 3):]

    # Ações de UI 
    def _set_btn_active(self, buttons, active_value):
        """Atualiza visual dos botões de seleção — evita repetição em 3 métodos."""
        for btn, v in buttons:
            active = v == active_value
            btn.configure(
                fg_color="#2d2b55" if active else "#12122a",
                text_color="#c4b5fd" if active else "#666688",
                border_color="#7c3aed" if active else "#333355",
            )

    def _paste_url(self):
        try:
            text = self.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, text)
        except Exception:
            pass

    def _select_type(self, t):
        self.download_type.set(t)
        is_video = t == "video"

        self._set_btn_active(
            [(self.btn_video, True), (self.btn_audio, False)], is_video
        )

        if is_video:
            self.audio_label.pack_forget()
            self.audio_frame.pack_forget()
            self.quality_label.pack(fill="x")
            self.quality_frame.pack(fill="x", pady=(6, 18))
        else:
            self.quality_label.pack_forget()
            self.quality_frame.pack_forget()
            self.audio_label.pack(fill="x")
            self.audio_frame.pack(fill="x", pady=(6, 18))

    def _select_quality(self, value):
        self.quality_var.set(value)
        self._set_btn_active(self.quality_buttons, value)

    def _select_audio_fmt(self, fmt):
        self.audio_var.set(fmt)
        self._set_btn_active(self.audio_buttons, fmt)

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self._download_folder)
        if folder:
            self._download_folder = folder
            self.dest_label.configure(text=self._shorten_path(folder))

    #  Download 
    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Atenção", "Cole uma URL antes de baixar.")
            return
        if self._is_downloading:
            return

        ffmpeg = get_ffmpeg_path()
        if ffmpeg is None:
            if not messagebox.askyesno(
                "FFmpeg não encontrado",
                "O ffmpeg.exe não foi encontrado.\n"
                "Vídeos podem ser baixados sem áudio.\n\n"
                "Deseja continuar mesmo assim?"
            ):
                return

        self._is_downloading = True
        self.download_btn.configure(state="disabled", text="Baixando...")
        self.progress_bar.set(0)
        self._set_status("Iniciando download...")

        # ffmpeg já resolvido aqui — não chama get_ffmpeg_path() de novo na thread
        threading.Thread(target=self._do_download, args=(url, ffmpeg), daemon=True).start()

    def _do_download(self, url, ffmpeg):
        is_audio = self.download_type.get() == "audio"

        ydl_opts = {
            "outtmpl": os.path.join(self._download_folder, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "noplaylist": True,
        }

        # Passa o diretório do ffmpeg (não o arquivo em si)
        if ffmpeg:
            ydl_opts["ffmpeg_location"] = os.path.dirname(ffmpeg)

        if is_audio:
            fmt = self.audio_var.get()
            ydl_opts["format"] = "bestaudio/best"
            if ffmpeg:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": fmt,
                    "preferredquality": "192",
                }]
        else:
            chosen = self.quality_var.get()
            if ffmpeg:
                ydl_opts["format"] = chosen
                ydl_opts["merge_output_format"] = "mp4"
            else:
                # Sem FFmpeg: formato pré-mesclado (com áudio, qualidade menor)
                ydl_opts["format"] = "best[ext=mp4]/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self._set_status("✓ Download concluído!")
            self.after(0, lambda: self.progress_bar.set(1))
        except Exception as e:
            self._set_status(f"Erro: {e}")
            self.after(0, lambda: messagebox.showerror("Erro no download", str(e)))
        finally:
            self._is_downloading = False
            self.after(0, lambda: self.download_btn.configure(
                state="normal", text="⬇   Baixar agora"
            ))

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()

            if total:
                pct = d.get("downloaded_bytes", 0) / total
                self.after(0, lambda p=pct: self.progress_bar.set(p))

            msg = f"Baixando... {d.get('_percent_str', '').strip()}"
            if speed:
                msg += f"  —  {speed}"
            if eta:
                msg += f"  —  Tempo Estimado {eta}"
            self._set_status(msg)

        elif d["status"] == "finished":
            self._set_status("Mesclando vídeo e áudio...")

    def _set_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text))


# Ponto de entrada
if __name__ == "__main__":
    app = App()
    app.mainloop()
