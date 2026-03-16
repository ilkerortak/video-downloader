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
            error_message = "Lütfen geçerli bir video bağlantısı girin."
        else:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    # --- KRİTİK ÇÖZÜM: Çerez dosyasını kullan ---
                    'cookiefile': 'cookies.txt', 
                    # --------------------------------------------
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    },
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        video_info = {
                            'title': info.get('title', 'Video'),
                            'url': info.get('url'),
                            'thumbnail': info.get('thumbnail')
                        }
            except Exception as e:
                print(f"Hata Detayı: {e}")
                error_message = "TikTok engeli aşılamadı. Lütfen çerez dosyasını güncelleyin veya linki kontrol edin."

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
