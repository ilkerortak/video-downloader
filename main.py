import yt_dlp
from flask import Flask, render_template, request, Response
import requests
import urllib.parse
import os

app = Flask(__name__)

# TIKTOK KÖPRÜSÜ
def get_tiktok_data(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, timeout=15).json()
        if res.get('code') == 0:
            data = res['data']
            return {'url': data['play'], 'title': data.get('title', 'TikTok'), 'thumb': data.get('cover'), 'platform': 'TikTok'}
    except: return None

# GENEL ÇEKİCİ (YouTube/Instagram için ekstra önlemli)
def get_general_video_data(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        # YouTube engellerini aşmak için en kritik ayarlar:
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'geo_bypass': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info: return None
        video_url = info.get('url')
        if not video_url and 'formats' in info:
            # En düşük kaliteli ama en ulaşılabilir olanı seçmeyi dener
            video_url = info['formats'][0].get('url')
        
        return {
            'url': video_url,
            'title': info.get('title', 'Video'),
            'thumb': info.get('thumbnail'),
            'platform': info.get('extractor_key', 'Sosyal Medya')
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            if "tiktok.com" in url:
                video_info = get_tiktok_data(url)
            else:
                video_info = get_general_video_data(url)
            
            if not video_info:
                error_message = "Sunucu şu an meşgul veya erişim engellendi. Lütfen 5 dakika sonra deneyin."
        except:
            error_message = "Erişim Engeli! Platform sunucuyu blokladı."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        r = requests.get(video_url, stream=True, timeout=30, verify=False)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except: return "Dosya çekilemedi.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
