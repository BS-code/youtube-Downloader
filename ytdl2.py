"""
YouTube Downloader - Modern Version (Final Fix)
Dibuat oleh: BUDI SUTOMO
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime


class ModernYouTubeDownloader:
    """Aplikasi downloader YouTube dengan desain modern"""

    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Set style
        self.setup_styles()
        
        # Variabel data
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="✅ Siap mengunduh...")

        # Variabel playlist & format
        self.is_playlist = tk.BooleanVar(value=False)
        self.playlist_type = tk.StringVar(value="video")
        self.format_var = tk.StringVar(value="video")

        # Mode download
        self.download_mode = tk.StringVar(value="single")

        # Batas download playlist
        self.playlist_limit = tk.IntVar(value=0)
        self.use_limit = tk.BooleanVar(value=False)

        # Status validasi URL
        self.url_valid = False
        self.current_info = None
        self.detected_type = None  # 'single' or 'playlist'

        # Data tracking
        self.cancel_download = False
        self.downloaded_files = []
        self.current_download = None
        
        # Placeholders untuk widget
        self.fetch_btn = None
        self.download_btn = None
        self.cancel_btn = None
        self.open_folder_btn = None
        self.single_frame = None
        self.playlist_frame = None
        self.single_video_radio = None
        self.single_mp3_radio = None
        self.playlist_video_radio = None
        self.playlist_mp3_radio = None
        self.single_mode_radio = None
        self.playlist_mode_radio = None
        self.info_text = None
        self.download_list = None
        self.progress_var = None
        self.progress_bar = None
        self.progress_percent = None
        self.progress_label = None
        self.limit_entry = None
        self.limit_check = None
        
        # Build UI
        self.setup_ui()
        
        # Set initial button states
        self._update_button_states()

    def setup_styles(self):
        """Mengatur style modern"""
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = '#f8f9fa'
        fg_color = '#2c3e50'
        accent_color = '#3498db'
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 9))
        style.configure('TLabelframe', background=bg_color, foreground=fg_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color, font=('Segoe UI', 9, 'bold'))
        style.configure('TButton', font=('Segoe UI', 9), padding=(10, 5))
        style.configure('TRadiobutton', background=bg_color, font=('Segoe UI', 9))
        style.configure('TCheckbutton', background=bg_color, font=('Segoe UI', 9))
        style.configure('Horizontal.TProgressbar', background=accent_color, troughcolor='#e0e0e0')

    def setup_ui(self):
        """Membangun UI modern"""
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        self._buat_header(main_frame)
        self._buat_url_section(main_frame)
        self._buat_info_section(main_frame)
        self._buat_options_section(main_frame)
        self._buat_download_list(main_frame)
        self._buat_progress_section(main_frame)
        self._buat_action_buttons(main_frame)
        self._buat_status_bar(main_frame)
        self._buat_credit(main_frame)

    def _buat_header(self, parent):
        header_frame = tk.Frame(parent, bg='#3498db', height=60)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🎬 YouTube Downloader", 
                        font=('Segoe UI', 14, 'bold'), bg='#3498db', fg='white')
        title.pack(side='left', padx=15, pady=15)
        
        subtitle = tk.Label(header_frame, text="By; Budi Sutomo || freeware",
                           font=('Segoe UI', 9), bg='#3498db', fg='#d4e6f1')
        subtitle.pack(side='left', padx=(0, 15), pady=15)

    def _buat_url_section(self, parent):
        frame = ttk.LabelFrame(parent, text="🔗 URL", padding=(10, 5))
        frame.pack(fill='x', pady=(0, 10))
        
        url_entry = ttk.Entry(frame, textvariable=self.url_var, font=('Segoe UI', 10))
        url_entry.pack(fill='x', pady=(0, 8))
        
        btn_frame = tk.Frame(frame, bg='#f8f9fa')
        btn_frame.pack(fill='x')
        
        self.fetch_btn = ttk.Button(btn_frame, text="📋 Ambil Info", command=self.fetch_info, width=15)
        self.fetch_btn.pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="🗑️ Clear", command=self.clear_fields, width=10).pack(side='left')

    def _buat_info_section(self, parent):
        frame = ttk.LabelFrame(parent, text="📊 Informasi", padding=(10, 5))
        frame.pack(fill='x', pady=(0, 10))
        
        self.info_text = tk.Text(frame, height=3, wrap=tk.WORD,
                                 font=('Segoe UI', 9), bg='white',
                                 relief='flat', borderwidth=1)
        self.info_text.pack(fill='x')
        self.info_text.insert(1.0, "Masukkan URL dan klik 'Ambil Info'")
        self.info_text.config(state='disabled')

    def _buat_options_section(self, parent):
        """Section opsi dengan mode mutually exclusive berdasarkan deteksi"""
        # Frame untuk memilih mode download
        mode_frame = tk.Frame(parent, bg='#f8f9fa')
        mode_frame.pack(fill='x', pady=(0, 10))
        
        mode_label = tk.Label(mode_frame, text="Pilih Mode Download:", 
                              bg='#f8f9fa', font=('Segoe UI', 9, 'bold'))
        mode_label.pack(anchor='w', pady=(0, 5))
        
        mode_radio_frame = tk.Frame(mode_frame, bg='#f8f9fa')
        mode_radio_frame.pack(fill='x', pady=(0, 5))
        
        self.single_mode_radio = ttk.Radiobutton(mode_radio_frame, text="🎬 Single Video",
                                                  variable=self.download_mode, value="single",
                                                  command=self._on_mode_changed)
        self.single_mode_radio.pack(side='left', padx=(0, 20))
        
        self.playlist_mode_radio = ttk.Radiobutton(mode_radio_frame, text="📁 Playlist",
                                                    variable=self.download_mode, value="playlist",
                                                    command=self._on_mode_changed)
        self.playlist_mode_radio.pack(side='left')
        
        # Frame untuk konten
        self.content_frame = tk.Frame(parent, bg='#f8f9fa')
        self.content_frame.pack(fill='x', pady=(0, 10))
        
        # Single frame
        self.single_frame = ttk.LabelFrame(self.content_frame, text="🎬 Opsi Single Video", padding=(10, 5))
        
        self.single_video_radio = ttk.Radiobutton(self.single_frame, text="🎬 Video (MP4)", 
                                                  variable=self.format_var, value="video")
        self.single_video_radio.pack(anchor='w', pady=2)
        
        self.single_mp3_radio = ttk.Radiobutton(self.single_frame, text="🎵 MP3 (Audio)", 
                                                variable=self.format_var, value="mp3")
        self.single_mp3_radio.pack(anchor='w', pady=2)
        
        # Playlist frame
        self.playlist_frame = ttk.LabelFrame(self.content_frame, text="📁 Opsi Playlist", padding=(10, 5))
        
        self.playlist_video_radio = ttk.Radiobutton(self.playlist_frame, text="🎬 Video semua",
                                                    variable=self.playlist_type, value="video")
        self.playlist_video_radio.pack(anchor='w', pady=2)
        
        self.playlist_mp3_radio = ttk.Radiobutton(self.playlist_frame, text="🎵 MP3 semua",
                                                  variable=self.playlist_type, value="mp3")
        self.playlist_mp3_radio.pack(anchor='w', pady=2)
        
        # Batas download playlist
        limit_frame = tk.Frame(self.playlist_frame, bg='#f8f9fa')
        limit_frame.pack(anchor='w', pady=(10, 0))
        
        self.limit_check = ttk.Checkbutton(limit_frame, text="Batasi jumlah download:",
                                           variable=self.use_limit, command=self._toggle_limit)
        self.limit_check.pack(side='left', padx=(0, 5))
        
        self.limit_entry = ttk.Entry(limit_frame, width=8, state='disabled')
        self.limit_entry.pack(side='left', padx=(0, 5))
        
        limit_label = tk.Label(limit_frame, text="video", bg='#f8f9fa', font=('Segoe UI', 8))
        limit_label.pack(side='left')
        
        info_label = tk.Label(limit_frame, text="(0 = tidak terbatas)", bg='#f8f9fa', 
                              font=('Segoe UI', 7), fg='gray')
        info_label.pack(side='left', padx=(5, 0))
        
        # Tampilkan default (single)
        self.single_frame.pack(fill='x')
        self.playlist_frame.pack_forget()
        
        # Location
        loc_frame = tk.Frame(parent, bg='#f8f9fa')
        loc_frame.pack(fill='x', pady=(10, 0))
        
        loc_label = tk.Label(loc_frame, text="💾 Lokasi:", bg='#f8f9fa', font=('Segoe UI', 9))
        loc_label.pack(side='left', padx=(0, 10))
        
        path_entry = tk.Entry(loc_frame, textvariable=self.download_path, 
                             font=('Segoe UI', 9), bg='white', relief='flat')
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Button(loc_frame, text="📂 Browse", command=self.browse_folder, width=10).pack(side='right')

    def _toggle_limit(self):
        """Toggle batas download playlist"""
        if self.use_limit.get():
            self.limit_entry.config(state='normal')
        else:
            self.limit_entry.config(state='disabled')
            self.playlist_limit.set(0)

    def _on_mode_changed(self):
        """Handler ketika mode download berubah"""
        if self.download_mode.get() == "single":
            self.single_frame.pack(fill='x')
            self.playlist_frame.pack_forget()
        else:
            self.single_frame.pack_forget()
            self.playlist_frame.pack(fill='x')
        self._update_button_states()

    def _buat_download_list(self, parent):
        frame = ttk.LabelFrame(parent, text="📋 Daftar Download", padding=(10, 5))
        frame.pack(fill='both', expand=True, pady=(0, 10))
        
        ctrl_frame = tk.Frame(frame, bg='#f8f9fa')
        ctrl_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Button(ctrl_frame, text="🗑️ Hapus Daftar", command=self.clear_download_list, width=15).pack(side='left', padx=(0, 10))
        ttk.Button(ctrl_frame, text="📋 Salin Daftar", command=self.copy_download_list, width=15).pack(side='left')
        
        self.download_list = tk.Text(frame, height=5, wrap=tk.WORD,
                                     font=('Segoe UI', 8), bg='white',
                                     relief='flat', borderwidth=1)
        self.download_list.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(self.download_list, orient='vertical', 
                                  command=self.download_list.yview)
        self.download_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        self.download_list.insert(1.0, "Belum ada file yang diunduh")
        self.download_list.config(state='disabled')

    def _buat_progress_section(self, parent):
        frame = tk.Frame(parent, bg='#f8f9fa')
        frame.pack(fill='x', pady=(0, 10))
        
        self.progress_label = tk.Label(frame, text="", bg='#f8f9fa', 
                                       font=('Segoe UI', 8), fg='#6c757d')
        self.progress_label.pack(anchor='w', pady=(0, 3))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, 
                                            maximum=100, mode='determinate',
                                            style='Horizontal.TProgressbar')
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        self.progress_percent = tk.Label(frame, text="0%", bg='#f8f9fa', 
                                         font=('Segoe UI', 8, 'bold'), fg='#3498db')
        self.progress_percent.pack(anchor='e')

    def _buat_action_buttons(self, parent):
        """Tombol dengan ukuran proporsional"""
        btn_frame = tk.Frame(parent, bg='#f8f9fa')
        btn_frame.pack(fill='x', pady=(10, 8))
        
        # Frame untuk tombol dengan lebar yang sama
        button_container = tk.Frame(btn_frame, bg='#f8f9fa')
        button_container.pack(expand=True, fill='x')
        
        # Tombol Download
        self.download_btn = tk.Button(button_container, text="⬇️ DOWNLOAD", 
                                     command=self.start_download,
                                     bg='#3498db', fg='white', font=('Segoe UI', 11, 'bold'),
                                     relief='flat', padx=30, pady=10,
                                     activebackground='#2980b9', activeforeground='white',
                                     cursor='hand2', state='disabled',
                                     width=15)
        self.download_btn.pack(side='left', expand=True, fill='x', padx=(0, 10))
        
        # Tombol Batal
        self.cancel_btn = tk.Button(button_container, text="❌ BATAL",
                                    command=self.cancel_download_func,
                                    bg='#e74c3c', fg='white', font=('Segoe UI', 11, 'bold'),
                                    relief='flat', padx=30, pady=10,
                                    activebackground='#c0392b', activeforeground='white',
                                    cursor='hand2', state='disabled',
                                    width=15)
        self.cancel_btn.pack(side='left', expand=True, fill='x', padx=(0, 10))
        
        # Tombol Buka Folder
        self.open_folder_btn = tk.Button(button_container, text="📁 BUKA FOLDER",
                                         command=self.open_folder,
                                         bg='#95a5a6', fg='white', font=('Segoe UI', 11, 'bold'),
                                         relief='flat', padx=30, pady=10,
                                         activebackground='#7f8c8d', activeforeground='white',
                                         cursor='hand2',
                                         width=15)
        self.open_folder_btn.pack(side='left', expand=True, fill='x')

    def _buat_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg='#e9ecef', height=30)
        status_frame.pack(fill='x', pady=(0, 5))
        status_frame.pack_propagate(False)
        
        status_icon = tk.Label(status_frame, text="▶️", bg='#e9ecef', fg='#28a745',
                               font=('Segoe UI', 9))
        status_icon.pack(side='left', padx=(10, 5), pady=5)
        
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               bg='#e9ecef', fg='#495057', font=('Segoe UI', 9))
        status_label.pack(side='left', pady=5)

    def _buat_credit(self, parent):
        credit_frame = tk.Frame(parent, bg='#f8f9fa')
        credit_frame.pack(fill='x')
        
        credit_text = "© 2024 YouTube Downloader | Created by BUDI SUTOMO | Freeware (No FFmpeg)"
        credit_label = tk.Label(credit_frame, text=credit_text,
                               bg='#f8f9fa', fg='#adb5bd', font=('Segoe UI', 8))
        credit_label.pack()

    def _update_button_states(self):
        """Update status berdasarkan deteksi URL"""
        if not hasattr(self, 'download_btn') or self.download_btn is None:
            return
            
        if self.url_valid:
            self.download_btn.config(state='normal')
            
            # Nonaktifkan mode yang tidak sesuai dengan deteksi
            if self.detected_type == 'single':
                self.playlist_mode_radio.config(state='disabled')
                self.single_mode_radio.config(state='normal')
                # Jika user mencoba pilih playlist, paksa ke single
                if self.download_mode.get() == 'playlist':
                    self.download_mode.set('single')
                    self._on_mode_changed()
            elif self.detected_type == 'playlist':
                self.single_mode_radio.config(state='disabled')
                self.playlist_mode_radio.config(state='normal')
                # Jika user mencoba pilih single, paksa ke playlist
                if self.download_mode.get() == 'single':
                    self.download_mode.set('playlist')
                    self._on_mode_changed()
            else:
                self.single_mode_radio.config(state='normal')
                self.playlist_mode_radio.config(state='normal')
            
            # Enable options based on mode
            if self.download_mode.get() == "single":
                self.single_video_radio.config(state='normal')
                self.single_mp3_radio.config(state='normal')
            else:
                self.playlist_video_radio.config(state='normal')
                self.playlist_mp3_radio.config(state='normal')
                self.limit_check.config(state='normal')
                if self.use_limit.get():
                    self.limit_entry.config(state='normal')
        else:
            self.download_btn.config(state='disabled')
            self.single_mode_radio.config(state='disabled')
            self.playlist_mode_radio.config(state='disabled')
            self.single_video_radio.config(state='disabled')
            self.single_mp3_radio.config(state='disabled')
            self.playlist_video_radio.config(state='disabled')
            self.playlist_mp3_radio.config(state='disabled')
            self.limit_check.config(state='disabled')
            self.limit_entry.config(state='disabled')

    def _reset_progress(self):
        if self.progress_var:
            self.progress_var.set(0)
            self.progress_percent.config(text="0%")
            self.progress_label.config(text="")

    def _update_progress(self, percent, speed=""):
        if self.progress_var:
            self.progress_var.set(percent)
            self.progress_percent.config(text=f"{percent:.0f}%")
            if speed:
                self.progress_label.config(text=f"Kecepatan: {speed}")
            else:
                self.progress_label.config(text=f"Mengunduh... {percent:.0f}%")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path.get())
        if folder:
            self.download_path.set(folder)

    def fetch_info(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Masukkan URL!")
            return

        self.fetch_btn.config(state='disabled')
        self.status_var.set("🔄 Mengambil informasi...")
        
        def ambil_info():
            try:
                import yt_dlp
                ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if 'entries' in info and info.get('_type') == 'playlist':
                        total = len(info['entries'])
                        teks = f"📁 PLAYLIST: {info.get('title', 'Unknown')}\n"
                        teks += f"📊 {total} video | 👤 {info.get('uploader', 'Unknown')}"
                        self.current_info = {'type': 'playlist', 'data': info, 'total': total}
                        self.detected_type = 'playlist'
                    else:
                        teks = f"🎬 SINGLE VIDEO: {info.get('title', 'Unknown')}\n"
                        teks += f"⏱️ Durasi: {info.get('duration_string', 'Unknown')} | 👁️ Views: {info.get('view_count', 0):,}"
                        self.current_info = {'type': 'single', 'data': info}
                        self.detected_type = 'single'
                    
                    self.root.after(0, lambda: self._set_url_valid(True))
                    self.root.after(0, lambda: self._update_info(teks))
                    self.root.after(0, self._update_button_states)
                    self.status_var.set("✅ Info berhasil diambil - Siap download")
                    
            except Exception as e:
                self.root.after(0, lambda: self._set_url_valid(False))
                # [FIX] Perbaikan: menggunakan method, bukan assignment langsung
                self.root.after(0, self._reset_detected_type)
                self.root.after(0, lambda: messagebox.showerror("Error", f"URL tidak valid!\n{str(e)}"))
                self.status_var.set("❌ URL tidak valid")
            finally:
                self.root.after(0, lambda: self.fetch_btn.config(state='normal'))
        
        threading.Thread(target=ambil_info, daemon=True).start()

    def _reset_detected_type(self):
        """Reset detected type"""
        self.detected_type = None

    def _set_url_valid(self, valid):
        self.url_valid = valid
        self._update_button_states()

    def _update_info(self, teks):
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, teks)
        self.info_text.config(state='disabled')

    def cancel_download_func(self):
        self.cancel_download = True
        self.status_var.set("⏹️ Membatalkan download...")
        self.cancel_btn.config(state='disabled')

    def start_download(self):
        if not self.url_valid:
            messagebox.showerror("Error", "Ambil info URL terlebih dahulu!")
            return
            
        url = self.url_var.get().strip()

        self.cancel_download = False
        self.downloaded_files = []
        self._reset_progress()
        
        self.download_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.fetch_btn.config(state='disabled')
        self.single_mode_radio.config(state='disabled')
        self.playlist_mode_radio.config(state='disabled')
        self.status_var.set("🎬 Memulai download...")

        def proses():
            try:
                import yt_dlp
                
                # Counter untuk playlist
                download_count = 0
                max_downloads = 0
                
                if self.download_mode.get() == "playlist" and self.use_limit.get():
                    try:
                        max_downloads = int(self.limit_entry.get())
                        if max_downloads <= 0:
                            max_downloads = 0
                    except ValueError:
                        max_downloads = 0
                
                def file_hook(d):
                    nonlocal download_count
                    
                    if self.cancel_download:
                        raise Exception("Download dibatalkan oleh user")
                    
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d:
                            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                            speed = d.get('_speed_str', '')
                            self.root.after(0, lambda p=percent, s=speed: self._update_progress(p, s))
                    elif d['status'] == 'finished':
                        filename = d.get('filename', '')
                        if filename:
                            title = os.path.basename(filename).rsplit('.', 1)[0]
                            ftype = "MP3" if filename.endswith('.mp3') else "VIDEO"
                            self.root.after(0, lambda t=title, ft=ftype: self._add_to_list(t, ft))
                            download_count += 1

                if self.download_mode.get() == "playlist":
                    self._download_playlist(url, file_hook, max_downloads)
                else:
                    self._download_single(url, file_hook)
                
                if not self.cancel_download:
                    self.root.after(0, self._download_complete)
                else:
                    self.root.after(0, self._download_cancelled)
                    
            except Exception as e:
                error_msg = str(e)
                if "dibatalkan" in error_msg.lower():
                    self.root.after(0, self._download_cancelled)
                else:
                    self.root.after(0, lambda: self._download_error(error_msg))
        
        self.current_download = threading.Thread(target=proses, daemon=True)
        self.current_download.start()

    def _add_to_list(self, title, ftype):
        if not self.cancel_download:
            waktu = datetime.now().strftime("%H:%M:%S")
            self.downloaded_files.append({'title': title, 'type': ftype, 'time': waktu})
            self._refresh_download_list()

    def _refresh_download_list(self):
        self.download_list.config(state='normal')
        self.download_list.delete(1.0, tk.END)
        
        if not self.downloaded_files:
            self.download_list.insert(1.0, "Belum ada file yang diunduh")
        else:
            header = f"Total: {len(self.downloaded_files)} file\n"
            header += "-" * 40 + "\n"
            self.download_list.insert(1.0, header)
            
            for i, f in enumerate(self.downloaded_files, 1):
                icon = "🎬" if f['type'] == "VIDEO" else "🎵"
                line = f"{i:2}. {icon} {f['title'][:50]}\n"
                self.download_list.insert(tk.END, line)
        
        self.download_list.config(state='disabled')

    def _download_single(self, url, hook):
        import yt_dlp
        fmt = self.format_var.get()
        ext = "mp3" if fmt == "mp3" else "%(ext)s"
        ydl_opts = {
            'outtmpl': os.path.join(self.download_path.get(), f'%(title)s.{ext}'),
            'progress_hooks': [hook],
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best' if fmt == "mp3" else 'best[ext=mp4]/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def _download_playlist(self, url, hook, max_downloads):
        import yt_dlp
        tipe = self.playlist_type.get()
        ext = "mp3" if tipe == "mp3" else "%(ext)s"
        
        opts = {
            'outtmpl': os.path.join(self.download_path.get(), f'%(playlist)s/%(playlist_index)s - %(title)s.{ext}'),
            'format': 'bestaudio/best' if tipe == "mp3" else 'best[ext=mp4]/best',
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [hook],
        }
        
        # Tambahkan batasan jika diperlukan
        if max_downloads > 0:
            opts['playlistend'] = max_downloads
            self.status_var.set(f"📁 Download playlist (max {max_downloads} video)...")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def _download_complete(self):
        self.progress_var.set(100)
        self.progress_percent.config(text="100%")
        self.progress_label.config(text="Download selesai!")
        
        self.download_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.fetch_btn.config(state='normal')
        self._update_button_states()
        self.status_var.set("✅ Download selesai!")
        
        msg = f"Download selesai!\n{len(self.downloaded_files)} file berhasil diunduh"
        messagebox.showinfo("Sukses", msg)

    def _download_cancelled(self):
        self._reset_progress()
        self.download_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.fetch_btn.config(state='normal')
        self._update_button_states()
        self.status_var.set("⏹️ Download dibatalkan")
        
        if self.downloaded_files:
            self._refresh_download_list()
            messagebox.showinfo("Info", f"Download dibatalkan.\n{len(self.downloaded_files)} file berhasil diunduh sebelum dibatalkan.")
        else:
            messagebox.showinfo("Info", "Download telah dibatalkan.")

    def _download_error(self, msg):
        self._reset_progress()
        self.download_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.fetch_btn.config(state='normal')
        self._update_button_states()
        self.status_var.set("❌ Download gagal!")
        messagebox.showerror("Error", msg)

    def open_folder(self):
        folder = self.download_path.get()
        if os.path.exists(folder):
            if os.name == 'nt':
                os.startfile(folder)
            else:
                subprocess.run(['xdg-open', folder])
        else:
            messagebox.showerror("Error", "Folder tidak ditemukan!")

    def clear_fields(self):
        self.cancel_download = False
        self.url_var.set("")
        self._set_url_valid(False)
        self.detected_type = None
        self._reset_progress()
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Masukkan URL dan klik 'Ambil Info'")
        self.info_text.config(state='disabled')
        self.download_mode.set("single")
        self.use_limit.set(False)
        self.playlist_limit.set(0)
        self.limit_entry.config(state='disabled')
        self.limit_entry.delete(0, tk.END)
        self.limit_entry.insert(0, "0")
        self._on_mode_changed()
        self.status_var.set("✅ Siap mengunduh...")

    def clear_download_list(self):
        if messagebox.askyesno("Konfirmasi", "Hapus daftar download?"):
            self.downloaded_files = []
            self._refresh_download_list()

    def copy_download_list(self):
        if not self.downloaded_files:
            messagebox.showinfo("Info", "Tidak ada daftar")
            return
        teks = f"YouTube Downloader\nTotal: {len(self.downloaded_files)} file\n\n"
        for i, f in enumerate(self.downloaded_files, 1):
            teks += f"{i}. {f['title']} [{f['type']}]\n"
        self.root.clipboard_clear()
        self.root.clipboard_append(teks)
        messagebox.showinfo("Sukses", "Daftar disalin!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernYouTubeDownloader(root)
    root.mainloop()
