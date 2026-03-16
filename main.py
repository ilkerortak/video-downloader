from flask import Flask, render_template, request
import yt_dlp
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            error_message = "Lütfen geçerli bir link girin."
        else:
            try:
                # yt-dlp ayarları (Hızlı ve sadece link çekme odaklı)
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_info = {
                        'title': info.get('title', 'Video'),
                        'url': info.get('url'),
                        'thumbnail': info.get('thumbnail')
                    }
            except Exception as e:
                # Hata oluşursa site çökmez, ekrana hata mesajı basar
                error_message = f"Bir hata oluştu: Link desteklenmiyor olabilir."
                print(f"Hata Detayı: {e}") # Loglarda görünmesi için

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    # Railway için port ayarı
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
