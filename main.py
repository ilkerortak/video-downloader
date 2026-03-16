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
                    # Çerez dosyasını mutlaka okumalı
                    'cookiefile': 'cookies.txt',
                    # TikTok'un mobil api'sini kullanmaya zorla
                    'extractor_args': {
                        'tiktok': {
                            'web_proxy': True,
                            'app_version': '33.1.4',
                            'manifest_app_version': '33.1.4',
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'com.zhiliaoapp.musically/2023301040 (Linux; U; Android 10; tr_TR; Samsung SM-G973N; Build/QP1A.190711.020; Cronet/58.0.2991.0)',
                        'Accept-Language': 'tr-TR,tr;q=0.9',
                    },
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        # TikTok bazen 'url' yerine 'formats' içinde link gönderir
                        video_url = info.get('url')
                        if not video_url and 'formats' in info:
                            video_url = info['formats'][-1].get('url')
                            
                        video_info = {
                            'title': info.get('title', 'Video'),
                            'url': video_url,
                            'thumbnail': info.get('thumbnail')
                        }
            except Exception as e:
                print(f"Hata Detayı: {e}")
                if "403" in str(e):
                    error_message = "TikTok sunucu erişimini reddetti. Farklı bir video linki deneyin veya çerez dosyasını tazeleyin."
                else:
                    error_message = "Video analiz edilemedi. Lütfen bağlantıyı kontrol edin."

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
