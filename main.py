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
                # TikTok'un yeni bot engellerini aşmak için agresif ayarlar
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                    # Varsa çerezleri kullan, yoksa hata verme
                    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                    # TikTok'u Android uygulamasıymış gibi davranmaya zorla
                    'impersonate': 'chrome', # Modern tarayıcı gibi davranır
                    'extractor_args': {
                        'tiktok': {
                            'app_version': '33.1.4',
                            'manifest_app_version': '33.1.4',
                        }
                    },
                    'http_headers': {
                        'User-Agent': 'com.zhiliaoapp.musically/2023301040 (Linux; U; Android 10; tr_TR; Samsung SM-G973N; Build/QP1A.190711.020; Cronet/58.0.2991.0)',
                    },
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        video_url = info.get('url')
                        # Bazı durumlarda URL 'formats' içindedir
                        if not video_url and 'formats' in info:
                            video_url = next((f['url'] for f in reversed(info['formats']) if f.get('vcodec') != 'none'), None)
                            
                        video_info = {
                            'title': info.get('title', 'Video'),
                            'url': video_url,
                            'thumbnail': info.get('thumbnail')
                        }
            except Exception as e:
                print(f"Hata Detayı: {e}")
                # Loglardaki hata mesajına göre kullanıcıya bilgi verelim
                if "status code 0" in str(e):
                    error_message = "TikTok şu an erişimi engelliyor. Lütfen 5-10 dakika sonra tekrar deneyin veya linki kontrol edin."
                else:
                    error_message = "Video analiz edilemedi. Bağlantı kısıtlı veya hatalı olabilir."

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
