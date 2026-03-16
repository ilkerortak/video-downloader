import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # --- 1. TIKTOK (Sorunsuz) ---
    if "tiktok.com" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if r.get('code') == 0:
                d = r['data']
                return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
        except: pass

    # --- 2. INSTAGRAM (Özel Engine) ---
    if "instagram.com" in url:
        # Sunucu bloklamasını aşmak için 3 farklı motoru sırayla deniyoruz
        engines = [
            f"https://api.cobalt.tools/api/json",
            f"https://api.vkrdownloader.com/server?vkr={url}",
            f"https://api.boxentriq.com/social/video?url={url}"
        ]
        
        # İlk olarak en güçlü olan Cobalt (Instagram için özel headers ile)
        try:
            res = requests.post(engines[0], 
                                headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                json={'url': url, 'vQuality': '720'}, timeout=12).json()
            if res.get('url'):
                return {'url': res['url'], 'title': 'Instagram Reels', 'thumb': 'https://img.icons8.com/fluency/96/instagram-new.png', 'platform': 'Instagram'}
        except: pass

        # Eğer ilk motor hata verirse, doğrudan indirme linki üreten alternatif
        try:
            r = requests.get(f"https://api.savefrom.net/api/v1/save?url={url}", timeout=10).json()
            if r.get('url'):
                return {'url': r['url'][0]['url'], 'title': 'Instagram Video', 'thumb': '', 'platform': 'Instagram'}
        except: pass

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            video_info = fetch_video(url)
    return render_template('index.html', video_info=video_info)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir')
    try:
        # Instagram'ın "403 Forbidden" hatasını aşmak için User-Agent ekliyoruz
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "İndirme şu an yapılamıyor.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
