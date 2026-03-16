import os
import yt_dlp
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import tempfile

app = Flask(__name__)
app.secret_key = "ilker_ortak_sakarya_54_premium"

def get_video_info(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Video'),
                'thumb': info.get('thumbnail'),
                'url': url
            }
    except: return None

def download_media(url, mode='video'):
    temp_dir = tempfile.gettempdir()
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
    }
    
    if mode == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
    except: return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        action = request.form.get('action') # 'info', 'video' veya 'mp3'
        
        if action == 'info':
            info = get_best_info = get_video_info(url)
            if info:
                session['video_preview'] = info
            else:
                session['error'] = "Bilgiler alınamadı!"
        
        elif action in ['video', 'mp3']:
            filepath = download_media(url, mode=action)
            if filepath and os.path.exists(filepath):
                return send_file(filepath, as_attachment=True)
            session['error'] = "İndirme başarısız!"
            
        return redirect(url_for('index'))
    
    preview = session.pop('video_preview', None)
    error = session.pop('error', None)
    return render_template('index.html', preview=preview, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
