from flask import Flask, render_template, request, redirect, url_for, session
import yt_dlp
import os
import requests # Artık hata vermeyecek

app = Flask(__name__)
app.secret_key = 'ilker_sakarya_54'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            session['error_message'] = "Lütfen bir link girin."
        else:
            try:
                # Proxy ayarı - Eğer çalışmazsa burayı boş bırakabiliriz
                # proxy_url = "http://ip:port" 
                
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    # 'proxy': proxy_url, # Proxy denemek istersen bu satırı aktif et
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
                        session.pop('error_message', None)
            except Exception as e:
                print(f"Hata: {e}")
                session['error_message'] = "TikTok erişimi hala kısıtlı. Çerezleri veya Proxy'yi kontrol edin."
                session.pop('video_info', None)
        
        return redirect(url_for('index'))

    video_info = session.pop('video_info', None)
    error_message = session.pop('error_message', None)
    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
