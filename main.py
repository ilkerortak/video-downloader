from flask import Flask, render_template, request, redirect, url_for, session
import yt_dlp
import os
import requests

app = Flask(__name__)
app.secret_key = 'ilker_sakarya_54_ultra_pro'

@app.route('/', methods=['GET', 'POST'])
def index():
    # Geçmiş listesini session'da başlat
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            session['error_message'] = "Lütfen bir link girin."
        else:
            video_data = None
            # TIKTOK ÖZEL ÇÖZÜM
            if "tiktok.com" in url:
                try:
                    api_url = f"https://www.tikwm.com/api/?url={url}"
                    res = requests.get(api_url).json()
                    if res.get('code') == 0:
                        d = res.get('data')
                        video_data = {
                            'title': d.get('title', 'TikTok Videosu')[:50] + "...",
                            'url': d.get('play'),
                            'thumb': d.get('cover'),
                            'platform': 'tiktok'
                        }
                except: pass
            
            # DİĞERLERİ
            else:
                try:
                    ydl_opts = {'quiet': True, 'format': 'best', 'noplaylist': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        video_data = {
                            'title': info.get('title', 'Video')[:50] + "...",
                            'url': info.get('url'),
                            'thumb': info.get('thumbnail'),
                            'platform': 'video'
                        }
                except: pass

            if video_data:
                session['video_info'] = video_data
                # Geçmişe ekle (En fazla 3 adet tutar)
                history = session.get('history', [])
                # Aynı video varsa tekrar ekleme
                if not any(h['url'] == video_data['url'] for h in history):
                    history.insert(0, video_data)
                    session['history'] = history[:3]
                session.pop('error_message', None)
            else:
                session['error_message'] = "Video çözülemedi."

        return redirect(url_for('index'))

    video_info = session.pop('video_info', None)
    error_message = session.pop('error_message', None)
    history = session.get('history', [])
    
    return render_template('index.html', video_info=video_info, error_message=error_message, history=history)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
