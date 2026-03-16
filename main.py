import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

# TIKTOK İÇİN ÖZEL API (403 ENGELİ YOK)
def get_tiktok_data(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, timeout=10).json()
        if res.get('code') == 0:
            data = res['data']
            return {'url': data['play'], 'title': data.get('title', 'TikTok'), 'thumb': data.get('cover'), 'platform': 'TikTok'}
    except: return None

# INSTAGRAM VE YOUTUBE İÇİN DIŞ KAYNAKLI API (SUNUCU BANINI AŞAR)
def get_external_api_data(url):
    # Bu API, Instagram ve YouTube için senin sunucun yerine videoyu çeker
    # Not: Bu tür servisler zaman zaman değişebilir, en stabili budur.
    try:
        # Alternatif bir downloader API'si kullanıyoruz
        api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
        res = requests.get(api_url, timeout=15).json()
        
        # API başarılı dönerse veriyi işle
        if res.get('data'):
            video_data = res['data']
            # En yüksek kaliteli MP4 linkini bul
            download_url = video_data['url']
            return {
                'url': download_url,
                'title': video_data.get('title', 'Sosyal Medya Videosu'),
                'thumb': video_data.get('thumbnail', ''),
                'platform': 'Sosyal Medya'
            }
    except Exception as e:
        print(f"API Hatası: {e}")
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            # TikTok için kendi özel köprüsü
            if "tiktok.com" in url:
                video_info = get_tiktok_data(url)
            # Instagram, YouTube, Facebook vb. için dış API
            else:
                video_info = get_external_api_data(url)
            
            if not video_info:
                error_message = "Video çekilemedi. Platform şu an erişimi kısıtlıyor olabilir."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    if not video_url: return "URL eksik", 400
    try:
        # İndirmeyi zorla
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "İndirme başlatılamadı.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
