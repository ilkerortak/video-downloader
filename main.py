import requests
from flask import Flask, render_template, request, Response, redirect, url_for, session
import urllib.parse
import os

app = Flask(__name__)
app.secret_key = "ilker_ortak_54_sakarya"

def fetch_video(url):
    # TIKTOK (Stabil devam)
    if "tiktok.com" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if r.get('code') == 0:
                d = r['data']
                return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok', 'method': 'direct'}
        except: pass

    # INSTAGRAM / YOUTUBE (Yeni Nesil JS Köprüsü)
    if any(x in url for x in ["instagram.com", "youtube.com", "youtu.be"]):
        return {'target_url': url, 'platform': 'Instagram' if 'instagram' in url else 'YouTube', 'method': 'js_bridge'}
    
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            video_info = fetch_video(url)
            if video_info:
                session['video_info'] = video_info
        return redirect(url_for('index'))
    
    video_info = session.pop('video_info', None)
    return render_template('index.html', video_info=video_info)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir')
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "Hata!", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
