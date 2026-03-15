from flask import Flask, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def get_channels():
    url = "https://raw.githubusercontent.com/Sflex0719/ZioGarmTara/main/ZioGarmTara.m3u"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        content = response.text
        
        channels = []
        # Split by #EXTINF: to get each channel block
        entries = content.split('#EXTINF:')
        
        for entry in entries[1:]:
            channel_data = {}
            
            # 1. Extract Title
            title_match = re.search(r',([^\n\r]+)', entry)
            channel_data['title'] = title_match.group(1).strip() if title_match else "Unknown"

            # 2. Extract Logo
            logo_match = re.search(r'tvg-logo="([^"]+)"', entry)
            channel_data['tvg_logo'] = logo_match.group(1) if logo_match else None

            # 3. Extract the User-Agent from EXTVLCOPT
            ua_match = re.search(r'#EXTVLCOPT:http-user-agent=([^\n\r]+)', entry)
            stream_ua = ua_match.group(1).strip() if ua_match else None

            # 4. Extract ClearKey/License
            clearkey_match = re.search(r'#KODIPROP:input_stream.adaptive.license_key=([^\n\r]+)', entry)
            channel_data['clearkey'] = clearkey_match.group(1).strip() if clearkey_match else None

            # 5. Extract Cookie
            cookie_match = re.search(r'Cookie=([^&\n\r]+)', entry)
            channel_data['cookie'] = cookie_match.group(1).strip() if cookie_match else None

            # 6. Extract Stream URL and append User-Agent
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            raw_url = next((line for line in reversed(lines) if line.startswith('http')), None)
            
            # If User-Agent exists, add it to the URL with |
            if raw_url and stream_ua:
                channel_data['url'] = f"{raw_url}|User-Agent={stream_ua}"
            else:
                channel_data['url'] = raw_url

            channels.append(channel_data)
            
        return jsonify(channels)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
