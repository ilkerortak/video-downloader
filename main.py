import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # LİSTE: Denenecek API servisleri
    # Birinci patlarsa ikinciye, o da patlarsa üçüncüye geçer.
    
    # 1. Deneme: TikWM (TikTok için zaten iyi)
    if "tiktok" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=8).json()
            if r.get('code') == 0:
                return {'url': r['data']['play'], 'title': r['data'].get('title', 'TikTok'), 'thumb': r['data'].get('cover')}
        except: pass

    # 2. Deneme: VKR Downloader (Genel servis)
    try:
        r = requests.get(f"https://api.vkrdownloader.com/server?vkr={url}", timeout=8).json()
        if r.get('data'):
            d = r['data']
            v_url = d['url'][0] if isinstance(d['url'], list) else d['url']
            return {'url': v_url, 'title': d.get('title', 'Video'), 'thumb': d.get('thumbnail', '')}
    except: pass

    # 3. Deneme: Alternatif bir açık kaynak API (Örnek: Cobalt benzeri yapılar)
    # Buraya başka API uçları eklenebilir.
    
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            video_info = fetch_video(url)
            if not video_info:
                # İşte senin gördüğün o hata burada tetikleniyor
                error_message = "Video bağlantısı şu an çözülemedi. Platform servisleri yoğun olabilir."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        r = requests.get(video_url, stream=True, timeout=20)
        return Response(r.iter_content(chunk_size=1024*1024),
                        mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "Hata!", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
