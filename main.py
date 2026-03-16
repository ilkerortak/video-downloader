import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

# 1. TIKTOK KÖPRÜSÜ (En stabili)
def get_tiktok_data(url):
    try:
        res = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
        if res.get('code') == 0:
            d = res['data']
            return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
    except: return None

# 2. INSTAGRAM KÖPRÜSÜ (Özel Instagram API'si)
def get_instagram_data(url):
    try:
        # Instagram engellerini aşmak için kullanılan alternatif bir servis
        api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
        res = requests.get(api_url, timeout=12).json()
        if res.get('data'):
            d = res['data']
            return {'url': d['url'], 'title': 'Instagram Videosu', 'thumb': d.get('thumbnail', ''), 'platform': 'Instagram'}
    except: return None

# 3. YOUTUBE KÖPRÜSÜ (Cobalt/Vail benzeri açık kaynaklı motorlar)
def get_youtube_data(url):
    try:
        # YouTube için sunucunu değil, bu köprüyü kullanıyoruz
        # Eğer bu API çalışmazsa 'y2mate' benzeri bir yapıya geçeceğiz
        api_url = f"https://api.boxentriq.com/social/video?url={url}"
        res = requests.get(api_url, timeout=12).json()
        if res.get('url'):
            return {'url': res['url'], 'title': res.get('title', 'YouTube Video'), 'thumb': res.get('thumbnail', ''), 'platform': 'YouTube'}
    except: return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            if "tiktok.com" in url:
                video_info = get_tiktok_data(url)
            elif "instagram.com" in url:
                video_info = get_instagram_data(url)
            elif "youtube.com" in url or "youtu.be" in url:
                video_info = get_youtube_data(url)
            else:
                # Diğerleri için Instagram köprüsünü dene (geneldir)
                video_info = get_instagram_data(url)
            
            if not video_info:
                error_message = "Platform erişimi geçici olarak kısıtladı. Lütfen 1 dakika sonra tekrar deneyin."
        except:
            error_message = "Beklenmedik bir hata oluştu. Linki kontrol edin."
            
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        # İndirmeyi zorlamak için doğrudan yönlendirme yapıyoruz
        # Eğer 403 alırsan 'requests.get' ile stream etmeye geri döneriz
        return Response(requests.get(video_url, stream=True).iter_content(chunk_size=1024*1024),
                        mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except:
        return "İndirme şu an yapılamıyor.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
