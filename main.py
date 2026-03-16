import requests
from flask import Flask, render_template, request, redirect, url_for, session, Response
import os

app = Flask(__name__)
app.secret_key = "ilker_ortak_sakarya_kesin_sonuc"

def fetch_video(url):
    url = url.strip()
    
    # YOUTUBE İÇİN SUNUCU TARAFLI ÇÖZÜM (En Garanti Yol)
    if any(x in url for x in ["youtube.com", "youtu.be"]):
        try:
            payload = {'url': url, 'vQuality': '720'}
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            r = requests.post('https://api.cobalt.tools/api/json', json=payload, headers=headers, timeout=15)
            data = r.json()
            if data.get('url'):
                return {'url': data['url'], 'platform': 'YouTube', 'method': 'direct', 'title': 'YouTube Videosu'}
        except: pass

    # TIKTOK
    if "tiktok.com" in url:
        return {'target_url': url, 'platform': 'TikTok', 'method': 'js_tiktok'}

    # INSTAGRAM (Hala en nazlısı, JS ile denemeye devam)
    if "instagram.com" in url or "reels" in url:
        return {'target_url': url, 'platform': 'Instagram', 'method': 'js_cobalt'}
        
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        video_info = fetch_video(url)
        if video_info:
            session['video_info'] = video_info
        return redirect(url_for('index'))
    
    video_info = session.pop('video_info', None)
    return render_template('index.html', video_info=video_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
