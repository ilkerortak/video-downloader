from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "ilker_sakarya_54_kesin_cozum"

def fetch_video(url):
    url = url.strip()
    # TikTok için özel işaret
    if "tiktok.com" in url:
        return {'target_url': url, 'platform': 'TikTok', 'type': 'tt'}
    # Instagram/YouTube için genel işaret
    if any(x in url for x in ["instagram.com", "reels", "youtube.com", "youtu.be"]):
        return {'target_url': url, 'platform': 'Sosyal Medya', 'type': 'social'}
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
