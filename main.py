from flask import Flask, render_template, request, redirect, url_for, session
import yt_dlp
import os
import requests

app = Flask(__name__)
app.secret_key = 'ilker_sakarya_54_kesin_cozum'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            session['error_message'] = "Lütfen bir bağlantı girin."
        else:
            # 1. YÖNTEM: TikTok API'si (En Garanti Yol)
            if "tiktok.com" in url:
                try:
                    # TikTok için ücretsiz bir API köprüsü kullanıyoruz
                    api_url = f"https://www.tikwm.com/api/?url={url}"
                    response = requests.get(api_url).json()
                    
                    if response.get('code') == 0:
                        data = response.get('data')
                        session['video_info'] = {
                            'title': data.get('title', 'TikTok Videosu'),
                            'url': data.get('play'), # Filigransız video linki
                        }
                        session.pop('error_message', None)
                    else:
                        session['error_message'] = "TikTok videosu şu an indirilemiyor."
                except Exception as e:
                    session['error_message'] = "API bağlantı hatası oluştu."
            
            # 2. YÖNTEM: Diğer Platformlar İçin yt-dlp
            else:
                try:
                    ydl_opts = {
                        'quiet': True,
                        'format': 'best',
                        'noplaylist': True,
                        'nocheckcertificate': True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info:
                            session['video_info'] = {
                                'title': info.get('title', 'Video Çözüldü'),
                                'url': info.get('url'),
                            }
                            session.pop('error_message', None)
                except:
                    session['error_message'] = "Video bilgileri alınamadı."

        return redirect(url_for('index'))

    video_info = session.pop('video_info', None)
    error_message = session.pop('error_message', None)
    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
