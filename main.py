import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # --- 1. TIKTOK (Sende zaten çalışıyor, aynen korundu) ---
    if "tiktok.com" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if r.get('code') == 0:
                d = r['data']
                return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
        except: pass

    # --- 2. YOUTUBE (En sağlam 2 motoru deniyoruz) ---
    elif "youtube.com" in url or "youtu.be" in url:
        # A) MOTOR 1: Cobalt (Gizli API üzerinden)
        try:
            payload = {'url': url, 'vQuality': '720'}
            # Cobalt'ın bazen değişen API uçlarını deniyoruz
            res = requests.post('https://api.cobalt.tools/api/json', 
                                headers={'Accept': 'application/json'}, 
                                json=payload, timeout=10).json()
            if res.get('url'):
                return {'url': res['url'], 'title': 'YouTube Video', 'thumb': 'https://www.gstatic.com/youtube/img/branding/youtubelogo/2x/youtube_logo_dark_v2021.png', 'platform': 'YouTube'}
        except: pass

        # B) MOTOR 2: VKR (Yedek)
        try:
            res = requests.get(f"https://api.vkrdownloader.com/server?vkr={url}", timeout=10).json()
            if res.get('data'):
                d = res['data']
                v_url = d['url'][0] if isinstance(d['url'], list) else d['url']
                return {'url': v_url, 'title': d.get('title', 'YouTube Video'), 'thumb': d.get('thumbnail', ''), 'platform': 'YouTube'}
        except: pass

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
                error_message = "Video bağlantısı şu an çözülemedi. Lütfen daha sonra tekrar deneyin."
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    try:
        # YouTube ve TikTok indirmeleri için basit yönlendirme
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "İndirme başarısız.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
