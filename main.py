import yt_dlp
from flask import Flask, render_template, request, Response
import requests
import urllib.parse
import os

app = Flask(__name__)

def get_video_data(url):
    # En üst düzey engel aşma parametreleri
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        # Çerez ve Header taklidi
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        },
        'nocheckcertificate': True,
        'geo_bypass': True, # Bölgesel engelleri aşmak için
        'socket_timeout': 15,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # TikTok kısa linklerini (vm.tiktok...) çözmek için
        info = ydl.extract_info(url, download=False)
        video_url = info.get('url')
        
        if not video_url and 'formats' in info:
            video_url = info['formats'][-1].get('url')

        return {
            'url': video_url,
            'title': info.get('title', 'HemenIndir_Video'),
            'thumb': info.get('thumbnail'),
            'platform': info.get('extractor_key', 'Video')
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                video_info = get_video_data(url)
            except Exception as e:
                print(f"Sistem Hatası: {e}")
                error_message = "Bu video şu an korunuyor. Lütfen başka bir link deneyin."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    
    if not video_url:
        return "URL eksik", 400

    try:
        # Proxy kanalında da aynı kimliği kullanıyoruz
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }
        
        # Requests ile videoyu parça parça çekiyoruz
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        r.raise_for_status()

        return Response(
            r.iter_content(chunk_size=1024*1024),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"
            }
        )
    except Exception as e:
        return "İndirme başarısız. Platform sunucuyu engelledi.", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
