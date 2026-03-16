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
                # TikTok ve diğer platformlar için en güncel ve güçlü ayarlar
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                    # HTTP Header bilgilerini bir tarayıcı gibi güncelledik
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                    },
                    # Bazı extractor (ayıştırıcı) ayarları
                    'extractor_args': {
                        'youtube': {'player_client': ['android', 'web']},
                        'tiktok': {'web_proxy': True}
                    }
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
                # Hata mesajını kullanıcıya daha açıklayıcı verelim
                if "403" in str(e) or "Forbidden" in str(e):
                    error_message = "TikTok erişimi geçici olarak reddetti. Birkaç dakika sonra tekrar deneyin veya farklı bir link test edin."
                else:
                    error_message = "Video bilgileri alınamadı. Linkin doğru olduğundan emin olun."

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
