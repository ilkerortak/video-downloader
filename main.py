import os
import yt_dlp
import tempfile
from flask import Flask, render_template, request, redirect, url_for, session, send_file

app = Flask(__name__)
app.secret_key = "ilker_sakarya_54_kesin_sistem"

def download_media(url, mode='video'):
    temp_dir = tempfile.gettempdir()
    
    # Railway ve Linux sunucularda ffmpeg'in muhtemel yolları
    ffmpeg_path = '/usr/bin/ffmpeg'
    if not os.path.exists(ffmpeg_path):
        ffmpeg_path = 'ffmpeg' # Sistem yolunda varsa direkt kullan

    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'ffmpeg_location': ffmpeg_path
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
        # En iyi video ve sesi birleştir, mp4 formatında zorla
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Medya bilgisini al ve indir
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if mode == 'mp3':
                # MP3 çevrimi sonrası dosya adını kontrol et
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
        action = request.form.get('action') # 'video' veya 'mp3'
        
        if not url:
            session['error'] = "Lütfen geçerli bir link yapıştırın."
            return redirect(url_for('index'))

        filepath = download_media(url, mode=action)
        
        if filepath and os.path.exists(filepath):
            try:
                # Dosya ismini temizle (Türkçe karakter sorunlarını önlemek için)
                original_name = os.path.basename(filepath)
                return send_file(
                    filepath, 
                    as_attachment=True, 
                    download_name=original_name
                )
            except Exception as e:
                session['error'] = f"Dosya gönderilirken bir hata oluştu: {str(e)}"
        else:
            session['error'] = "HATA: Son işlem: ffprobe ve ffmpeg bulunamadı. Lütfen nixpacks.toml dosyasını kontrol edin."
            
        return redirect(url_for('index'))
    
    error = session.pop('error', None)
    return render_template('index.html', error=error)

if __name__ == '__main__':
    # Railway için port ayarı
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
