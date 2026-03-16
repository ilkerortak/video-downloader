import requests
from flask import Flask, render_template, request, redirect, url_for, session, Response
import urllib.parse
import os

app = Flask(__name__)
# Session verilerini güvenli tutmak için gerekli anahtar
app.secret_key = "ilker_ortak_sakarya_54_ozel_key"

def fetch_video(url):
    """
    Linkleri analiz eder ve arayüze (JS'ye) hangi yöntemle 
    indirileceği bilgisini gönderir.
    """
    url = url.strip()
    
    # 1. TIKTOK ANALİZİ
    if "tiktok.com" in url:
        return {
            'target_url': url, 
            'platform': 'TikTok', 
            'method': 'tiktok'
        }
    
    # 2. INSTAGRAM ANALİZİ (Reels, Post, TV)
    elif "instagram.com" in url or "reels" in url:
        return {
            'target_url': url, 
            'platform': 'Instagram', 
            'method': 'cobalt'
        }
    
    # 3. YOUTUBE ANALİZİ
    elif any(x in url for x in ["youtube.com", "youtu.be"]):
        return {
            'target_url': url, 
            'platform': 'YouTube', 
            'method': 'cobalt'
        }
        
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            video_info = fetch_video(url)
            if video_info:
                # Sayfa yenilendiğinde "Formu Yeniden Gönder" hatası almamak için 
                # veriyi session'a atıp yönlendirme yapıyoruz.
                session['video_info'] = video_info
        return redirect(url_for('index'))
    
    # Sayfa GET ile yüklendiğinde session'da veri varsa al ve session'dan temizle
    video_info = session.pop('video_info', None)
    return render_template('index.html', video_info=video_info)

# TikTok gibi doğrudan sunucu üzerinden çekilmesi gereken dosyalar için yedek köprü
@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)
        return Response(
            r.iter_content(chunk_size=1024*1024), 
            mimetype="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"}
        )
    except Exception as e:
        return f"İndirme sırasında bir hata oluştu: {str(e)}", 500

if __name__ == '__main__':
    # Railway ve benzeri platformlar için PORT ayarı
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
