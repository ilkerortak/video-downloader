from flask import Flask, render_template, request, redirect, url_for, session
import yt_dlp
import os
import requests

app = Flask(__name__)
app.secret_key = 'ilker_gizli_anahtar_54'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            session['error_message'] = "Lütfen geçerli bir video bağlantısı girin."
        else:
            try:
                # Önce standart yt-dlp ile deniyoruz
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    },
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        session['video_info'] = {
                            'title': info.get('title', 'Video'),
                            'url': info.get('url'),
                        }
            except Exception as e:
                # Eğer yt-dlp 403 verirse, TikTok Oembed API'sini deniyoruz (YEDEK PLAN)
                if "403" in str(e) and "tiktok" in url:
                    try:
                        oembed_url = f"https://www.tiktok.com/oembed?url={url}"
                        response = requests.get(oembed_url).json()
                        if 'title' in response:
                             # Not: Oembed video linkini direkt vermez, 
                             # ama en azından bağlantının yaşadığını kanıtlar.
                             # Buraya alternatif bir indirme API'si entegre edilebilir.
                             session['error_message'] = "TikTok şu an bu sunucuyu engelliyor. Lütfen tarayıcı eklentisi kullanarak indirmeyi deneyin."
                        else:
                             session['error_message'] = "TikTok erişimi reddetti. IP adresi engelli."
                    except:
                        session['error_message'] = "TikTok şu an erişime kapalı."
                else:
                    session['error_message'] = "Video analiz edilemedi."
        
        return redirect(url_for('index'))

    video_info = session.pop('video_info', None)
    error_message = session.pop('error_message', None)
    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
