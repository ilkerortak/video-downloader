import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def get_video_info(url):
    # Eğer link TikTok ise direkt TikWM'ye git
    if "tiktok.com" in url:
        try:
            res = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if res.get('code') == 0:
                d = res['data']
                return {'url': d['play'], 'title': d.get('title', 'TikTok'), 'thumb': d.get('cover'), 'platform': 'TikTok'}
        except: pass

    # Instagram, YouTube ve diğerleri için ana API
    # Birinci servis: vkrdownloader
    try:
        api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
        res = requests.get(api_url, timeout=12).json()
        if res.get('data'):
            d = res['data']
            # Link bazen liste olarak gelebilir, kontrol edelim
            final_url = d['url'][0] if isinstance(d['url'], list) else d['url']
            return {
                'url': final_url, 
                'title': d.get('title', 'Sosyal Medya Videosu'), 
                'thumb': d.get('thumbnail', ''), 
                'platform': 'Video'
            }
    except: pass

    # Eğer yukarıdaki çalışmazsa ikinci servis: ayon (YouTube ağırlıklı)
    try:
        # Bu sadece bir örnektir, alternatif API'lar eklenebilir
        pass
    except: pass

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    
    if request.method == 'POST':
        # Formdan gelen 'url' değerini al ve temizle
        url = request.form.get('url', '').strip()
        
        if not url:
            error_message = "Lütfen geçerli bir link yapıştırın."
        else:
            video_info = get_video_info(url)
            if not video_info:
                error_message = "Video bağlantısı şu an çözülemedi. Linkin gizli olmadığından emin olun."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024),
                        mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except:
        return "İndirme başlatılamadı.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
