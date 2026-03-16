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
        format_type = request.form.get('format_type') # 'video' veya 'audio'
        
        if not url:
            error_message = "Lütfen geçerli bir video bağlantısı girin."
        else:
            try:
                # Format seçimine göre yt-dlp ayarı
                # audio seçilirse sadece en iyi sesi, video seçilirse en iyi birleşik formatı alır
                format_code = 'bestaudio/best' if format_type == 'audio' else 'best'
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': format_code,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    },
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        video_info = {
                            'title': info.get('title', 'Medya Dosyası'),
                            'url': info.get('url'),
                            'thumbnail': info.get('thumbnail'),
                            'type': 'Müzik (MP3/Ses)' if format_type == 'audio' else 'Video (MP4)'
                        }
            except Exception as e:
                print(f"Hata: {e}")
                error_message = "Bağlantı analiz edilemedi. Bu video gizli olabilir veya link desteklenmiyor olabilir."

    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
