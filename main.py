from flask import Flask, render_template, request, redirect, url_for, session
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'ilker_sakarya_54_ozel'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            session['error_message'] = "Lütfen bir bağlantı girin."
        else:
            try:
                # TikTok'un en güncel engellerini aşmak için ayarlar
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'format': 'best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    # Çerez dosyası varsa kullan
                    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                    # TikTok'u gerçek bir cihaz olduğuna ikna etmek için:
                    'http_headers': {
                        'User-Agent': 'com.zhiliaoapp.musically/2023301040 (Linux; U; Android 10; tr_TR; Samsung SM-G973N; Build/QP1A.190711.020; Cronet/58.0.2991.0)',
                        'Accept': '*/*',
                        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                    },
                    'extractor_args': {
                        'tiktok': {
                            'app_version': '33.1.4',
                            'manifest_app_version': '33.1.4',
                        }
                    }
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        video_url = info.get('url')
                        # Eğer direkt URL yoksa formatlardan en iyisini seç
                        if not video_url and 'formats' in info:
                            video_url = info['formats'][-1].get('url')
                            
                        session['video_info'] = {
                            'title': info.get('title', 'Video Başarıla Çözüldü'),
                            'url': video_url,
                        }
                        session.pop('error_message', None)
            except Exception as e:
                print(f"Hata Detayı: {e}")
                if "403" in str(e):
                    session['error_message'] = "TikTok şu an sunucu IP'sini engelliyor. Lütfen 5 dk sonra tekrar deneyin."
                else:
                    session['error_message'] = "Video bilgileri alınamadı."
                session.pop('video_info', None)
        
        return redirect(url_for('index'))

    video_info = session.pop('video_info', None)
    error_message = session.pop('error_message', None)
    return render_template('index.html', video_info=video_info, error_message=error_message)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
