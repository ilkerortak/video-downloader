import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

# --- VİDEO ÇEKME MOTORLARI ---

def fetch_video(url):
    """
    Farklı platformlar için en uygun API köprüsünü seçer.
    """
    # 1. TIKTOK İÇİN ÖZEL MOTOR (TikWM)
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

    # 2. INSTAGRAM, YOUTUBE VE DİĞERLERİ (VKR & Genel Motor)
    try:
        # Bu API sunucunun IP engelini aşmak için aracı olur
        api_url = f"https://api.vkrdownloader.com/server?vkr={url}"
        r = requests.get(api_url, timeout=12).json()
        
        if r.get('data'):
            d = r['data']
            # Link bazen liste bazen string dönebilir, kontrol edelim
            v_url = d['url'][0] if isinstance(d['url'], list) else d['url']
            
            # YouTube bazen çok fazla format döner, MP4 olanı bulmaya çalışalım
            return {
                'url': v_url, 
                'title': d.get('title', 'Sosyal Medya Videosu'), 
                'thumb': d.get('thumbnail', ''),
                'platform': 'Sosyal Medya'
            }
    except: pass

    return None

# --- ROUTER (SAYFA YÖNETİMİ) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    
    # Sadece 'İndir' butonuna basıldığında işlem yap
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        
        if not url:
            error_message = "Lütfen bir video bağlantısı yapıştırın."
        else:
            # Videoyu çekmeye çalış
            video_info = fetch_video(url)
            
            # Eğer link var ama video bulunamadıysa hatayı şimdi göster
            if not video_info:
                error_message = "Video bağlantısı şu an çözülemedi. Linkin gizli olmadığından emin olun."
    
    # Sayfa ilk açıldığında (GET) error_message ve video_info None olduğu için hata görünmez.
    return render_template('index.html', video_info=video_info, error_message=error_message)

# --- İNDİRME KÖPRÜSÜ (PROXY) ---

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'hemenindir_video')
    
    if not video_url:
        return "Geçersiz istek.", 400

    try:
        # İndirme sırasında platformu kandırmak için gerçekçi bir kimlik
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
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
    # Railway veya Yerel Port ayarı
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
