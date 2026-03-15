from flask import Flask, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def get_channels():
    url = "https://raw.githubusercontent.com/Sflex0719/ZioGarmTara/main/ZioGarmTara.m3u"
    try:
        response = requests.get(url)
        content = response.text
        
        channels = []
        entries = content.split('#EXTINF:')
        
        for entry in entries[1:]:
            channel_data = {}
            title_match = re.search(r',([^\n\r]+)', entry)
            channel_data['title'] = title_match.group(1).strip() if title_match else "Unknown"

            logo_match = re.search(r'tvg-logo="([^"]+)"', entry)
            channel_data['tvg_logo'] = logo_match.group(1) if logo_match else None

            clearkey_match = re.search(r'#KODIPROP:input_stream.adaptive.license_key=([^\n\r]+)', entry)
            channel_data['clearkey'] = clearkey_match.group(1) if clearkey_match else None

            cookie_match = re.search(r'Cookie=([^&\n\r]+)', entry)
            channel_data['cookie'] = cookie_match.group(1) if cookie_match else None

            # Correctly finding the URL line
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            channel_data['url'] = lines[-1] if lines else None

            channels.append(channel_data)
            
        return jsonify(channels)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
  
