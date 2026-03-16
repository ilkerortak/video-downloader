import requests
from flask import Flask, render_template, request, Response
import urllib.parse
import os

app = Flask(__name__)

def get_tiktok_video(url):
    # TikTok engelini aşmak için TikWM API'sini (ücretsiz) kullanıyoruz
    api_url = f"https://www.tikwm.com/api/?url={url}"
    response = requests.get(api_url).json()
    
    if response.get('code') == 0:
        data = response['data']
        return {
            'url': data['play'], # Filigransız video linki
            'title': data.get('title', 'TikTok Video'),
            'thumb': data.get('cover'),
            'platform': 'TikTok'
        }
    raise Exception("TikTok videosu çekilemedi.")

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error_message = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # Eğer link tiktok içeriyorsa özel API'yi kullan
                if "tiktok.com" in url:
                    video_info = get_tiktok_video(url)
                else:
                    error_message = "Şimdilik sadece TikTok destekleniyor (Proxy önlemi)."
            except Exception as e:
                error_message = "TikTok engeline takıldık. Lütfen az sonra tekrar deneyin."
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

@app.route('/proxy_download')
def proxy_download():
    video_url = request.args.get('url')
    video_title = request.args.get('title', 'video')
    
    try:
        r = requests.get(video_url, stream=True, timeout=30)
        return Response(
            r.iter_content(chunk_size=1024*1024),
            mimetype="video/mp4",
            headers={"Content-Disposition": f"attachment; filename={urllib.parse.quote(video_title)}.mp4"}
        )
    except:
        return "İndirme başarısız.", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
