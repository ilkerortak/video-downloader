import yt_dlp
from flask import Flask, render_template, request, Response
import requests
import urllib.parse
import os

app = Flask(__name__)

# TikTok için özel köprü (403 engelini aşmak için)
def get_tiktok_data(url):
    api_url = f"https://www.tikwm.com/api/?url={url}"
    res = requests.get(api_url).json()
    if res.get('code') == 0:
        data = res['data']
        return {
            'url': data['play'],
            'title': data.get('title', 'TikTok Video'),
            'thumb': data.get('cover'),
            'platform': 'TikTok'
        }
    return None

# Diğer platformlar (YouTube, Instagram) için standart çekici
def get_general_video_data(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_url = info.get('url')
        if not video_url and 'formats' in info:
            video_url = info['formats'][-1].get('url')
        
        return {
            'url': video_url,
            'title': info.get('title', 'Video'),
            'thumb': info.get('thumbnail'),
            'platform': info.get('extractor_key', 'Video')
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # Linkin hangi platforma ait olduğunu kontrol et
                if "tiktok.com" in url:
                    video_info = get_tiktok_data(url)
                else:
                    video_info = get_general_video_data(url)
                
                if not video_info:
                    error_message = "Video bilgileri çekilemedi."
            except Exception as e:
                print(f"Hata: {e}")
                error_message = "Bu video şu an indirilemiyor (Erişim Engeli)."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    
    if not video_url: return "URL eksik", 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk: yield chunk

        return Response(
            generate(),
            mimetype="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"}
        )
    except Exception as e:
        return f"İndirme hatası: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
