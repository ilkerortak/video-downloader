import os
import yt_dlp
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, send_file

app = Flask(__name__)
app.secret_key = "ilker_sakarya_54_kesin_sistem"

def download_media(url, mode='video'):
    temp_dir = tempfile.gettempdir()
    
    # FFmpeg yolunu kontrol et
    ffmpeg_path = '/usr/bin/ffmpeg'
    if not os.path.exists(ffmpeg_path):
        ffmpeg_path = 'ffmpeg'

    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'ffmpeg_location': ffmpeg_path,
        'cookiefile': 'cookies.txt', # Instagram için çerez dosyası
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if mode == 'mp3':
                base, _ = os.path.splitext(filename)
                actual_mp3 = base + ".mp3"
                if os.path.exists(actual_mp3):
                    return actual_mp3
                return filename
            return filename
    except Exception as e:
        print(f"Sistem Hatası: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        action = request.form.get('action')
        
        if not url:
            session['error'] = "Lütfen geçerli bir link yapıştırın."
            return redirect(url_for('index'))

        filepath = download_media(url, mode=action)
        
        if filepath and os.path.exists(filepath):
            try:
                return send_file(
                    filepath, 
                    as_attachment=True, 
                    download_name=os.path.basename(filepath)
                )
            except Exception as e:
                session['error'] = f"Dosya gönderim hatası: {str(e)}"
        else:
            session['error'] = "İndirme başarısız. FFmpeg veya Çerez hatası olabilir."
            
        return redirect(url_for('index'))
    
    error = session.pop('error', None)
    return render_template('index.html', error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
