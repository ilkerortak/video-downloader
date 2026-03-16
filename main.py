from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "ilker_ortak_sakarya_54"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            # Savefrom'un kullandığı formatta platform tespiti
            platform = "Video"
            if "instagram" in url: platform = "Instagram"
            if "tiktok" in url: platform = "TikTok"
            if "youtube" in url or "youtu.be" in url: platform = "YouTube"
            
            session['video_info'] = {
                'target_url': url,
                'platform': platform
            }
        return redirect(url_for('index'))
    
    video_info = session.pop('video_info', None)
    return render_template('index.html', video_info=video_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
