import tkinter
import customtkinter
from tkinter import filedialog
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.innertube import _default_clients
from pytube import cipher
import re

# Fix for client version issues
_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

# Custom throttling function


def get_throttling_function_name(js: str) -> str:
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"
    )


cipher.get_throttling_function_name = get_throttling_function_name

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

        # Open a file dialog to select a save location
        save_path = filedialog.askdirectory()
        if not save_path:
            print("Download canceled.")
            return

        if video:
            video.download(output_path=save_path)
            print(f"Download complete! Video saved to: {save_path}")
        else:
            print("No suitable video stream found.")
    except RegexMatchError:
        print("Invalid YouTube link. Please check the URL.")
    except Exception as e:
        print(f"An error occurred: {e}")


# System settings
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("dark-blue")

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
