import os
import yt_dlp
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, send_file, send_from_directory

app = Flask(__name__)
app.secret_key = "ilker_ortak_sakarya_54_final"

def download_media(url, mode='video'):
    temp_dir = tempfile.gettempdir()
    
    ffmpeg_path = '/usr/bin/ffmpeg'
    if not os.path.exists(ffmpeg_path):
        ffmpeg_path = 'ffmpeg'

    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'ffmpeg_location': ffmpeg_path,
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
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
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        action = request.form.get('action')
        
        if not url:
            session['error'] = "Lütfen bir link yapıştırın."
            return redirect(url_for('index'))

        filepath = download_media(url, mode=action)
        
        if filepath and os.path.exists(filepath):
            # KESİN ÇÖZÜM: Dosyayı burada doğrudan göndermek yerine, 
            # Android'in yakalayabileceği bir GET rotasına yönlendiriyoruz.
            filename = os.path.basename(filepath)
            return redirect(url_for('serve_file', filename=filename))
        else:
            session['error'] = "İndirme başarısız."
            return redirect(url_for('index'))
    
    error = session.pop('error', None)
    return render_template('index.html', error=error)

# YENİ ROTA: Android ve Tarayıcılar dosyayı buradan 'GET' ile çekecek
@app.route('/get-media/<path:filename>')
def serve_file(filename):
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    if os.path.exists(filepath):
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4' if filename.endswith('.mp4') else 'audio/mpeg'
        )
    else:
        return "Dosya sunucuda bulunamadı veya silindi.", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
