import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # --- 1. TIKTOK MOTORU (DOKUNULMADI - AYNI KALDI) ---
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

    # --- 2. YOUTUBE MOTORU (YENİ VE GÜÇLENDİRİLMİŞ) ---
    elif "youtube.com" in url or "youtu.be" in url:
        try:
            # Cobalt API'ye istek gönderiyoruz
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                'url': url,
                'vQuality': '720', # Hızlı ve kaliteli sonuç için
                'filenameStyle': 'basic'
            }
            
            # Cobalt'ın ana API ucuna bağlanıyoruz
            res = requests.post('https://api.cobalt.tools/api/json', headers=headers, json=payload, timeout=15).json()
            
            # Cobalt 'stream' veya 'redirect' dönerse başarılıdır
            if res.get('status') in ['stream', 'redirect', 'success']:
                video_url = res.get('url')
                return {
                    'url': video_url,
                    'title': 'YouTube Videosu',
                    'thumb': 'https://www.gstatic.com/youtube/img/branding/youtubelogo/2x/youtube_logo_dark_v2021.png', # YouTube Logosu
                    'platform': 'YouTube'
                }
        except Exception as e:
            print(f"YouTube Hatası: {e}")
            pass

    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            error_message = "Lütfen bir video bağlantısı yapıştırın."
        else:
            video_info = fetch_video(url)
            if not video_info:
                error_message = "Video şu an çekilemedi. YouTube veya link erişime kapalı olabilir."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    
    if not video_url:
        return "Geçersiz istek.", 400

    try:
        # YouTube videolarını indirirken bazen 'User-Agent' şarttır
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        
        return Response(
            r.iter_content(chunk_size=1024*1024),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"
            }
        )
    except:
        return "Dosya sunucudan çekilemedi.", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
