from flask import Flask, render_template, request, redirect, url_for, session
import yt_dlp
import os

app = Flask(__name__)
# Session kullanabilmek için gizli bir anahtar belirlemeliyiz
app.secret_key = 'ilker_gizli_anahtar_54'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            session['error_message'] = "Lütfen geçerli bir video bağlantısı girin."
        else:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    },
                    'nocheckcertificate': True,
                    'geo_bypass': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        # Bilgileri session'a kaydediyoruz
                        session['video_info'] = {
                            'title': info.get('title', 'Video'),
                            'url': info.get('url'),
                        }
                        session.pop('error_message', None) # Varsa eski hatayı sil
            except Exception as e:
                session['error_message'] = "Video analiz edilemedi. Lütfen tekrar deneyin."
                session.pop('video_info', None) # Varsa eski videoyu sil
        
        # Form gönderildikten sonra sayfayı REFRESH (Yönlendir) yapıyoruz
        return redirect(url_for('index'))

    # GET isteği geldiğinde (Sayfa ilk açıldığında veya F5 yapıldığında)
    video_info = session.pop('video_info', None)
    error_message = session.pop('error_message', None)
    
    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
