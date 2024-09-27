from customtkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from pytube import YouTube, exceptions, Stream
from PIL import Image
from io import BytesIO
from requests import get # type: ignore
import threading, re
from os import path
from urllib.error import HTTPError

set_appearance_mode("dark")

root = CTk()
root.title("YouTube Downloader")
root.minsize(800, 600)
root.resizable(False, False)

CTkLabel(root, text=" YouTube Downloader", font=("TkDefaultFont", 30, "bold")).pack(pady=2)

link_frame = CTkFrame(root, fg_color="transparent")
link_frame.pack(pady=10)

CTkLabel(link_frame, text="Paste the link of a YouTube video here.").pack()
entry = CTkEntry(link_frame, 350, 32, 20, placeholder_text="https://www.youtube.com/watch...")
entry.pack(pady=2)

def on_progress(stream: Stream, chunk: bytes, bytes_remaining: int):
    downloaded = stream.filesize - bytes_remaining
    percent_complete = downloaded / stream.filesize
    progress_bar.set(percent_complete)

def download(Format: str):
    if Format == "Audio":
        def x():
            try:
                default_save_path = path.join(path.expanduser("~"), "Desktop")
                save_path = askdirectory(initialdir=default_save_path, title="Choose a place to save your audio.")
                if save_path:
                    download_button.pack_forget()
                    progress_bar.pack(pady=2)
                    progress_bar.set(0)
                    video.streams.first().download(save_path, video.title+".mp3", max_retries=5)
                else: return
            except exceptions.MaxRetriesExceeded:
                showerror("Error", "Error occured during download: maximum retries exceeded.\n\nPossible problems:\nNo internet connection or a pending API update.")
                progress_bar.pack_forget()
                download_button.pack(pady=2)
                return
            except HTTPError:
                showerror("Error", "Error occured during download: HTTP Error 400 (bad request)\n\nPossible problems:\nPending API update.")
                progress_bar.pack_forget()
                download_button.pack(pady=2)
                return
        threading.Thread(target=x).start()
    if Format == "Thumbnail":
        def x():
            try:
                default_save_path = path.join(path.expanduser("~"), "Desktop")
                save_path = askdirectory(initialdir=default_save_path, title="Choose a file to save your thumbnail in.")
                def y():
                    download_button.configure(text="Please wait...")
                    with open(path.join(save_path, re.sub(r'[\\/*?:"<>|]', "", video.title)+".png"), "wb") as image: image.write(get(video.thumbnail_url).content)
                    download_button.configure(text="Download complete!")
                    root.after(2000, lambda: download_button.configure(text="Download"))
                if save_path: threading.Thread(target=y).start()
                else: return
            except exceptions.MaxRetriesExceeded:
                showerror("Error", "Error occured during download: maximum retries exceeded.\n\nPossible problems:\nNo internet connection or a pending API update.")
                progress_bar.pack_forget()
                download_button.pack(pady=2)
                return
            except HTTPError:
                showerror("Error", "Error occured during download: HTTP Error 400 (bad request)\n\nPossible problems:\nPending API update.")
                progress_bar.pack_forget()
                download_button.pack(pady=2)
                return
        threading.Thread(target=x).start()
    if Format == "Video":
        def x():
            try:
                default_save_path = path.join(path.expanduser("~"), "Desktop")
                save_path = askdirectory(initialdir=default_save_path, title="Choose a place to save your audio.")
                if save_path:
                    download_button.pack_forget()
                    progress_bar.pack(pady=2)
                    progress_bar.set(0)
                    video.streams.get_highest_resolution().download(save_path, video.title+".mp3", max_retries=5)
                else: return
            except exceptions.MaxRetriesExceeded:
                showerror("Error", "Error occured during download: maximum retries exceeded.\n\nPossible problems:\nNo internet connection or a pending API update.")
                progress_bar.pack_forget()
                download_button.pack(pady=2)
                return
            except HTTPError:
                showerror("Error", "Error occured during download: HTTP Error 400 (bad request)\n\nPossible problems:\nPending API update.")
                progress_bar.pack_forget()
                download_button.pack(pady=2)
                return
        threading.Thread(target=x).start()

def load():
    global video, download_button, progress_bar
    if not entry: return
    try: video = YouTube(entry.get(), on_progress)
    except: return

    for slave in preview_frame.slaves():
        slave.destroy()
    preview_frame.pack_forget()

    x = CTkLabel(root, text="Please wait...")
    x.pack(pady=10)

    vid_format = StringVar(root, "Audio", "vid_format")

    def load_thumbnail():
        global download_button, progress_bar
        thumbnail_file = Image.open(BytesIO(get(video.thumbnail_url).content))
        thumbnail = CTkImage(thumbnail_file, thumbnail_file, (427, 240))
        x.destroy()
        CTkLabel(preview_frame, text="\n" + video.title, image=thumbnail, compound=TOP).pack(pady=5)
        options = CTkSegmentedButton(preview_frame, 200, 32, 15, values=["Audio", "Video", "Thumbnail"], variable=vid_format)
        options.pack(pady=10)
        download_button = CTkButton(preview_frame, text="Download", command=lambda: download(vid_format.get()))
        download_button.pack(pady=2)
        progress_bar = CTkProgressBar(preview_frame, 280, 24)
        preview_frame.pack(side=BOTTOM, pady=3)

    threading.Thread(target=load_thumbnail).start()

CTkButton(link_frame, 20, 20, 20, text="Load Video", command=load).pack(pady=2)

preview_frame = CTkFrame(root, 600, 425, 12, fg_color="transparent")
preview_frame.propagate(False)

root.mainloop()
