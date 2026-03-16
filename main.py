import yt_dlp
from flask import Flask, render_template, request, Response
import requests
import urllib.parse
import os

app = Flask(__name__)

# Video verilerini çeken fonksiyon
def get_video_data(url):
    # TikTok ve YouTube için en sağlam ayarlar
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'referer': 'https://www.tiktok.com/',
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Video linkini bulma
        video_url = info.get('url')
        if not video_url and 'formats' in info:
            # En son (genelde en kaliteli) formatı al
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
                video_info = get_video_data(url)
            except Exception as e:
                print(f"Hata: {e}")
                error_message = "Video bulunamadı. Linki kontrol edin veya daha sonra tekrar deneyin."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

# TELEFONA DİREKT İNDİRTEN KÖPRÜ (PROXY)
@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    
    if not video_url:
