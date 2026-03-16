import os, yt_dlp, tempfile
from flask import Flask, render_template, request, redirect, url_for, session, send_file

app = Flask(__name__)
app.secret_key = "ilker_ortak_sakarya_54"

def download_media(url, mode='video'):
    temp_dir = tempfile.gettempdir()
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
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
            original_file = ydl.prepare_filename(info)
            
            if mode == 'mp3':
                # Dosya uzantısını ne olursa olsun .mp3'e zorla
                actual_mp3 = os.path.splitext(original_file)[0] + ".mp3"
                return actual_mp3
            return original_file
    except Exception as e:
        print(f"Hata detayı: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        action = request.form.get('action') # 'video' veya 'mp3'
        
        if url:
            filepath = download_media(url, mode=action)
            if filepath and os.path.exists(filepath):
                # download_name kullanarak tarayıcıya dosya türünü net bildiriyoruz
                return send_file(
                    filepath, 
                    as_attachment=True, 
                    download_name=os.path.basename(filepath)
                )
            session['error'] = "Dosya işlenemedi. Linki kontrol edip tekrar dene."
        return redirect(url_for('index'))
    
    error = session.pop('error', None)
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
