import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # --- 1. TIKTOK MOTORU (STABİL) ---
    if "tiktok.com" in url:
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if r.get('code') == 0:
                d = r['data']
                return {
                    'url': d['play'], 
                    'title': d.get('title', 'TikTok Videosu'), 
                    'thumb': d.get('cover'),
                    'platform': 'TikTok'
                }
        except: pass

    # --- 2. YOUTUBE MOTORU (GÜNCELLENMİŞ) ---
    elif "youtube.com" in url or "youtu.be" in url:
        try:
            # Alternatif YouTube API Servisi
            api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
            res = requests.get(api_url, timeout=15).json()
            if res.get('data'):
                d = res['data']
                v_url = d['url'][0] if isinstance(d['url'], list) else d['url']
                return {
                    'url': v_url,
                    'title': d.get('title', 'YouTube Videosu'),
                    'thumb': d.get('thumbnail', 'https://www.gstatic.com/youtube/img/branding/youtubelogo/2x/youtube_logo_dark_v2021.png'),
                    'platform': 'YouTube'
                }
        except: pass

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        
        # Sadece bir link girilmişse işlem yapıyoruz
        if url:
            video_info = fetch_video(url)
            # Link girilmiş ama video bulunamamışsa hata ver
            if not video_info:
                error_message = "Video şu an çekilemedi. Linki kontrol edin veya platformun gizli olmadığından emin olun."
        # Link girilmeden basıldıysa error_message None kalır, uyarı çıkmaz.
            
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    if not video_url: return "Hata", 400
    try:
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "Hata", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
