import requests
from flask import Flask, render_template, request, Response, redirect, url_for, session
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = "ilker_54_sakarya_ultimate"

def get_best_stream(url):
    # Bu aşamada en güçlü ve stabil motoru kullanıyoruz
    try:
        payload = {"url": url, "vQuality": "720"}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        # Tek bir API yerine çalışan en sağlam tüneli buluyoruz
        r = requests.post("https://api.cobalt.tools/api/json", json=payload, headers=headers, timeout=15)
        return r.json().get('url')
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            stream_url = get_best_stream(url)
            if stream_url:
                session['video_info'] = {'url': stream_url, 'platform': 'Medya'}
            else:
                session['video_info'] = {'error': True}
        return redirect(url_for('index'))
    
    video_info = session.pop('video_info', None)
    return render_template('index.html', video_info=video_info)

# ASIL SİHİR BURADA: Instagram'ın engelleyemediği tünel
@app.route('/download_tunnel')
def download_tunnel():
    video_url = request.args.get('url')
    if not video_url: return "Link bulunamadı", 400
    
    try:
        # Sunucun videoyu "izleyici" gibi talep eder
        req = requests.get(video_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        return Response(req.iter_content(chunk_size=1024*1024), 
                        content_type=req.headers.get('Content-Type'),
                        headers={"Content-Disposition": "attachment; filename=HemenIndir_Video.mp4"})
    except:
        return "İndirme tünelinde hata oluştu", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
