import tkinter
import customtkinter
from pytube import YouTube
from typing import Literal
import os

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    print(f'{percentage:.2f}% downloaded')


def merge_audio(video_with_audio, new_audio, output_video):
    import subprocess
    # Combine the new audio with the video
    merge_cmd = f"ffmpeg -y -i '{video_with_audio}' -i '{new_audio}' -c:v copy -map 0:v:0 -map 1:a:0 -shortest '{output_video}'"
    subprocess.call(merge_cmd, shell=True)


def downloadVid():
    url = link.get()
    resolution = "highest-available"  # Change this based on user input if needed
    include_audio = True  # Change this based on user input if needed

    video_filename = "video.mp4"
    audio_filename = "audio.mp3"

    if os.path.exists(video_filename):
        print("Deleting temp video file...")
        os.remove(video_filename)

    if os.path.exists(audio_filename):
        print("Deleting temp audio file...")
        os.remove(audio_filename)

    print("Setting stream...")
    yt = YouTube(url)
    yt.register_on_progress_callback(on_progress)

    # Filter streams by resolution and format
    video = yt.streams.filter(
        progressive=False, file_extension='mp4').order_by('resolution').desc()

    if resolution == "highest-available":
        video = video.first()
        print(f"Highest available resolution is {video.resolution}...")
    elif resolution == "lowest-available":
        video = video.last()
        print(f"Lowest available resolution is {video.resolution}...")
    else:
        desired_res = int(resolution.replace('p', ''))
        diff_list = [(abs(desired_res - int(stream.resolution.replace('p', ''))), stream)
                     for stream in video]
        diff_list.sort(key=lambda x: x[0])
        video = diff_list[0][1]
        if video.resolution != resolution:
            print(
                f"{resolution} resolution is not available, using {video.resolution} instead...")
        else:
            print(f"Selected resolution is {resolution}...")

    print('Downloading video...')
    video.download(filename=video_filename)

    if include_audio:
        print('Downloading audio...')
        audios = yt.streams.filter(
            only_audio=True).order_by('abr').desc().first()
        audios.download(filename=audio_filename)
        print('Merging audio...')
        merge_audio(video_filename, audio_filename, "output.mp4")
        print('Done! Video saved as output.mp4')
    else:
        print('Done! Video saved as video.mp4')


# System settings
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

# App frame
app = customtkinter.CTk()
app.geometry("720x480")
app.title("YouTube Downloader")

# Adding UI Elements
title = customtkinter.CTkLabel(app, text="Insert a YouTube link")
title.pack(padx=10, pady=10)

# Link input
url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
link.pack()

# Download button
download = customtkinter.CTkButton(app, text="Download", command=downloadVid)
download.pack(padx=10, pady=10)

# Run app
app.mainloop()
