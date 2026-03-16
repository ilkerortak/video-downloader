
import os
import yt_dlp
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import tempfile

app = Flask(__name__)
app.secret_key = "ilker_ortak_final_boss_54"

def download_video(url):
    # Geçici bir dosya yolu oluşturuyoruz
    temp_dir = tempfile.gettempdir()
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'ffmpeg_location': ffmpeg_path,
        # ÇEREZ DOSYASINI BURADA TANITIYORUZ
        'cookiefile': 'cookies.txt', 
        # Instagram engeline karşı kullanıcı gibi davranma:
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"Hata: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            filepath = download_video(url)
            if filepath and os.path.exists(filepath):
                # Dosyayı bulduk, şimdi indirme rotasına gönderiyoruz
                return send_file(filepath, as_attachment=True)
            else:
                session['error'] = "Video çözülemedi. Linkin gizli olmadığından emin ol!"
        return redirect(url_for('index'))
    
    error = session.pop('error', None)
    return render_template('index.html', error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
