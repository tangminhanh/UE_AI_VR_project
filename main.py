import tkinter
import customtkinter
from pytube import YouTube
from pytube.exceptions import RegexMatchError

# Function to download YouTube video


def downloadVid():
    try:
        ytLink = link.get()
        ytObject = YouTube(ytLink)
        video = ytObject.streams.get_highest_resolution()
        video = ytObject.streams.filter(progressive=True, file_extension='mp4')\
                                .order_by('resolution')\
                                .desc()\
                                .first()
        if video:
            video.download()
            print("Download complete!")
        else:
            print("No suitable video stream found.")
    except RegexMatchError:
        print("Invalid YouTube link. Please check the URL.")
    except Exception as e:
        print(f"An error occurred: {e}")


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
