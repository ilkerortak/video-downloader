import os, yt_dlp, tempfile
from flask import Flask, render_template, request, redirect, url_for, session, send_file

app = Flask(__name__)
app.secret_key = "ilker_sakarya_54_kesin_cozum"

def download_media(url, mode='video'):
    temp_dir = tempfile.gettempdir()
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
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
            # Önce indir
            info = ydl.extract_info(url, download=True)
            # İndirilen dosyanın yolunu al
            filename = ydl.prepare_filename(info)
            
            if mode == 'mp3':
                # MP3 modunda yt-dlp uzantıyı otomatik değiştirir, kontrol edelim
                base, _ = os.path.splitext(filename)
                potential_mp3 = base + ".mp3"
                if os.path.exists(potential_mp3):
                    return potential_mp3
                return filename # Eğer MP3 oluşmadıysa orijinali gönder (hata vermesin)
            
            return filename
    except Exception as e:
        print(f"HATA DETAYI: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        action = request.form.get('action') # 'video' veya 'mp3'
        
        if not url:
            session['error'] = "Lütfen bir link yapıştırın!"
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
                session['error'] = f"Gönderim hatası: {str(e)}"
        else:
            session['error'] = "Dosya işlenemedi. Linki kontrol edip tekrar dene."
            
        return redirect(url_for('index'))
    
    error = session.pop('error', None)
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
