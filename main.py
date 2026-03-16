import yt_dlp
from flask import Flask, render_template, request, Response
import requests
import urllib.parse
import os

app = Flask(__name__)

# Gelişmiş Header Ayarları (403 ve Varnish Engelleri İçin)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.tiktok.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

def get_video_data(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': HEADERS['User-Agent'],
        'referer': 'https://www.tiktok.com/',
        'nocheckcertificate': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_url = info.get('url')
        if not video_url and 'formats' in info:
            video_url = info['formats'][-1].get('url')

        return {
            'url': video_url,
            'title': info.get('title', 'Video'),
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
                error_message = "Erişim Reddedildi (403). Lütfen farklı bir link deneyin."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir')
    
    if not video_url:
        return "URL eksik", 400

    try:
        # İndirme isteğinde tüm Header paketini gönderiyoruz
        r = requests.get(video_url, headers=HEADERS, stream=True, timeout=30, verify=False)
        r.raise_for_status()

        def generate():
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4",
                "Content-Type": "video/mp4"
            }
        )
    except Exception as e:
        print(f"Proxy Hatası: {e}")
        return "Sunucu bağlantıyı reddetti (Varnish 403).", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
