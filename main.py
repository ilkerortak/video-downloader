import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def fetch_video(url):
    # --- 1. TIKTOK MOTORU (DOKUNULMADI) ---
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

    # --- 2. YOUTUBE MOTORU (ALTERNATİF GÜÇLÜ KÖPRÜ) ---
    elif "youtube.com" in url or "youtu.be" in url:
        try:
            # YouTube için farklı bir API sağlayıcısı deniyoruz
            # Bu servis YouTube linkini analiz edip MP4 adresini döner
            api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
            res = requests.get(api_url, timeout=15).json()
            
            if res.get('data'):
                d = res['data']
                # En kaliteli video linkini yakala
                v_url = d['url'][0] if isinstance(d['url'], list) else d['url']
                return {
                    'url': v_url,
                    'title': d.get('title', 'YouTube Videosu'),
                    'thumb': d.get('thumbnail', 'https://www.gstatic.com/youtube/img/branding/youtubelogo/2x/youtube_logo_dark_v2021.png'),
                    'platform': 'YouTube'
                }
        except:
            # Eğer üstteki patlarsa son çare olarak bu basit köprüyü dene
            try:
                alt_res = requests.get(f"https://api.boxentriq.com/social/video?url={url}", timeout=10).json()
                if alt_res.get('url'):
                    return {
                        'url': alt_res['url'],
                        'title': alt_res.get('title', 'YouTube Video'),
                        'thumb': alt_res.get('thumbnail', ''),
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
        if not url:
            error_message = "Lütfen bir video bağlantısı yapıştırın."
        else:
            video_info = fetch_video(url)
            if not video_info:
                error_message = "YouTube şu an yoğun veya link hatalı. Lütfen tekrar deneyin."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    
    if not video_url: return "Geçersiz istek.", 400

    try:
        # YouTube videoları için özel yönlendirme (Direct Download)
        # Bazı YouTube linkleri doğrudan indirmeye izin verir, bazıları proxy gerektirir
        if "googlevideo.com" in video_url:
            # YouTube sunucuları proxy üzerinden çekilmeyi bazen engeller, direkt yönlendirelim
            return Response(requests.get(video_url, stream=True).iter_content(chunk_size=1024*1024),
                            mimetype="video/mp4",
                            headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
        
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(r.iter_content(chunk_size=1024*1024), mimetype="video/mp4",
                        headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"})
    except:
        return "İndirme başlatılamadı.", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
