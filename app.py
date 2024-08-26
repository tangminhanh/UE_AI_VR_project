from flask import Flask, request, render_template, send_file
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.innertube import _default_clients
from pytube import cipher
import re
import os
import tempfile

app = Flask(__name__)

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        yt_link = request.form['link']
        try:
            yt_object = YouTube(yt_link)
            video = yt_object.streams.filter(progressive=True, file_extension='mp4')\
                                     .order_by('resolution')\
                                     .desc()\
                                     .first()

            if video:
                # Create a temporary directory to save the video
                temp_dir = tempfile.mkdtemp()
                video_path = video.download(output_path=temp_dir)

                return send_file(video_path, as_attachment=True)
            else:
                return "No suitable video stream found.", 400
        except RegexMatchError:
            return "Invalid YouTube link. Please check the URL.", 400
        except Exception as e:
            return f"An error occurred: {e}", 500

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
