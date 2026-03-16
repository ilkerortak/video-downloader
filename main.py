import yt_dlp
from flask import Flask, render_template, request, send_file, Response
import requests
from io import BytesIO
import urllib.parse

app = Flask(__name__)

# Video bilgilerini çeken ana fonksiyon
def get_video_data(url):
    # yt-dlp ayarları: En iyi kaliteyi bul ama indirme, sadece bilgi getir
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Bazı platformlarda doğrudan URL gelmeyebilir, formatları kontrol et
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
                video_info = get_video_data(url)
            except Exception as e:
                print(f"Hata: {e}")
                error_message = "Video bulunamadı veya bu platform henüz desteklenmiyor."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

# TELEFONA DİREK İNDİRMEYİ SAĞLAYAN KÖPRÜ (PROXY)
@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    
    if not video_url:
        return "Geçersiz URL", 400

    try:
        # Videoyu sunucu üzerinden çekiyoruz
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        r = requests.get(video_url, headers=headers, stream=True, timeout=10)
        
        # Tarayıcıya indirme komutu gönderen Response yapısı
        return Response(
            r.content,
            mimetype="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"
            }
        )
    except Exception as e:
        return f"İndirme sırasında bir hata oluştu: {str(e)}", 500

if __name__ == '__main__':
    # Railway veya Yerel çalışma ayarı
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
