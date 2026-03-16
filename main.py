import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

# 1. TIKTOK (Sorunsuz çalışıyor)
def get_tiktok_data(url):
    try:
        res = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
        if res.get('code') == 0:
            d = res['data']
            return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
    except: return None

# 2. INSTAGRAM (Alternatif Motor)
def get_instagram_data(url):
    try:
        # SnapInsta benzeri bir motorun API ucunu deniyoruz
        api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
        res = requests.get(api_url, timeout=12).json()
        
        # vkr bazen farklı formatlarda döner, veriyi dikkatli çekelim
        if res.get('data'):
            d = res['data']
            # Eğer 'url' listeyse ilkini al, değilse direkt al
            v_url = d['url'] if isinstance(d['url'], str) else d['url'][0]
            return {
                'url': v_url, 
                'title': 'Instagram Videosu', 
                'thumb': d.get('thumbnail', ''), 
                'platform': 'Instagram'
            }
    except: return None

# 3. YOUTUBE (Yeni Köprü)
def get_youtube_data(url):
    try:
        # YouTube için daha hızlı sonuç veren bir API ucu
        # 'cobalt' benzeri açık kaynaklı bir servistir
        api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
        res = requests.get(api_url, timeout=12).json()
        if res.get('data'):
            d = res['data']
            return {
                'url': d['url'], 
                'title': d.get('title', 'YouTube Video'), 
                'thumb': d.get('thumbnail', ''), 
                'platform': 'YouTube'
            }
    except: return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                if "tiktok.com" in url:
                    video_info = get_tiktok_data(url)
                elif "instagram.com" in url:
                    video_info = get_instagram_data(url)
                elif "youtube.com" in url or "youtu.be" in url:
                    video_info = get_youtube_data(url)
                else:
                    video_info = get_instagram_data(url) # Genel çekici

                if not video_info:
                    error_message = "Video bağlantısı şu an çözülemedi. Linkin gizli olmadığından emin olun."
            except:
                error_message = "Sistem şu an bu videoyu göremiyor."
            
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        # Videoyu doğrudan tarayıcıya "akıtıyoruz"
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024),
                        mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except:
        return "İndirme başlatılamadı.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
