from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url')
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_info = {
                'title': info.get('title'),
                'url': info.get('url') # Doğrudan indirme linki
            }
    return render_template('index.html', video_info=video_info)

if __name__ == '__main__':
    app.run(debug=True)
