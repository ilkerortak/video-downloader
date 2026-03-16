import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # TIKTOK (Dokunulmadı, canavar gibi devam)
    if "tiktok.com" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if r.get('code') == 0:
                d = r['data']
                return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
        except: pass

    # YOUTUBE & INSTAGRAM (Hata almamak için arayüze paslıyoruz)
    # Eğer link bunlardan biriyse, Python tarafında işlem yapıp vakit kaybetmeyelim
    if "youtube.com" in url or "youtu.be" in url or "instagram.com" in url:
        return {'url': 'UI_HANDLED', 'platform': 'Social', 'target_url': url}

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
                error_message = "Geçersiz veya desteklenmeyen bağlantı."
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "Hata!", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
