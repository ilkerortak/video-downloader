import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # --- TIKTOK ---
    if "tiktok.com" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if r.get('code') == 0:
                d = r['data']
                return {'url': d['play'], 'title': d.get('title', 'TikTok Videosu'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
        except: pass

    # --- YOUTUBE & INSTAGRAM (TikTok Tarzı Bilgi Çeker) ---
    if any(x in url for x in ["youtube.com", "youtu.be", "instagram.com"]):
        try:
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            payload = {'url': url, 'vQuality': '720'}
            res = requests.post('https://api.cobalt.tools/api/json', headers=headers, json=payload, timeout=12).json()
            
            if res.get('status') in ['stream', 'redirect', 'success']:
                # YouTube için küçük resim oluşturma (TikTok gibi görünmesi için)
                thumb = "https://img.icons8.com/fluency/96/video.png"
                if "youtube.com" in url or "youtu.be" in url:
                    video_id = url.split('v=')[-1] if 'v=' in url else url.split('/')[-1]
                    thumb = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

                return {
                    'url': res.get('url'),
                    'title': 'Video İçeriği Hazır',
                    'thumb': thumb,
                    'platform': 'Sosyal Medya'
                }
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
                error_message = "Video bulunamadı. Lütfen linki kontrol edin."
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir')
    try:
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "Hata!", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
