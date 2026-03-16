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
                # Gelişmiş yt-dlp ayarları (TikTok ve diğerleri için)
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    # Sunucunun bot olarak algılanmasını engellemek için tarayıcı bilgileri:
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                    },
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'geo_bypass': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Video bilgilerini çek
                    info = ydl.extract_info(url, download=False)
                    
                    # Eğer video bilgisi başarıyla alındıysa
                    if info:
                        video_info = {
                            'title': info.get('title', 'Video'),
                            'url': info.get('url'),
                            'thumbnail': info.get('thumbnail')
                        }
                    else:
                        error_message = "Video bilgileri alınamadı. Link gizli veya hatalı olabilir."
                        
            except Exception as e:
                # Hata durumunda loglara yaz ve kullanıcıya mesaj ver
                print(f"Sistem Hatası: {e}")
                error_message = "Bu video indirilemedi. Desteklenmeyen bir site veya kısıtlı bir içerik olabilir."

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    # Railway ve diğer platformlar için port ayarı
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
