from flask import Flask, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/')
def get_channels():
    # The source M3U URL
    m3u_url = "https://raw.githubusercontent.com/Sflex0719/ZioGarmTara/main/ZioGarmTara.m3u"
    
    # Header to fetch the M3U file itself from GitHub
    fetch_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
    }

    try:
        response = requests.get(m3u_url, headers=fetch_headers, timeout=15)
        response.raise_for_status()
        content = response.text
        
        channels = []
        # Split the content into blocks starting with #EXTINF
        entries = content.split('#EXTINF:')
        
        for entry in entries[1:]:
            channel_data = {}
            
            # 1. Extract Channel Title
            title_match = re.search(r',([^\n\r]+)', entry)
            channel_data['title'] = title_match.group(1).strip() if title_match else "Unknown"

            # 2. Extract Logo URL
            logo_match = re.search(r'tvg-logo="([^"]+)"', entry)
            channel_data['tvg_logo'] = logo_match.group(1) if logo_match else None

            # 3. Extract the specific Stream User-Agent (from EXTVLCOPT)
            ua_match = re.search(r'#EXTVLCOPT:http-user-agent=([^\n\r]+)', entry)
            stream_ua = ua_match.group(1).strip() if ua_match else None

            # 4. Extract ClearKey (handles both inputstream and input_stream formats)
            ck_regex = r'#KODIPROP:input_?stream\.adaptive\.license_key=([^\n\r]+)'
            clearkey_match = re.search(ck_regex, entry)
            channel_data['clearkey'] = clearkey_match.group(1).strip() if clearkey_match else None

            # 5. Extract Cookie from #EXTHTTP JSON string
            cookie_match = re.search(r'"cookie":"([^"]+)"', entry)
            channel_data['cookie'] = cookie_match.group(1).strip() if cookie_match else None

            # 6. Extract Stream URL and append the User-Agent using the | separator
            lines = [l.strip() for l in entry.split('\n') if l.strip()]
            raw_url = None
            # Look for the line that starts with http (usually the last line)
            for line in reversed(lines):
                if line.startswith('http'):
                    raw_url = line
                    break
            
            # Combine URL with User-Agent if found
            if raw_url and stream_ua:
                channel_data['url'] = f"{raw_url}|User-Agent={stream_ua}"
            else:
                channel_data['url'] = raw_url

            channels.append(channel_data)
            
        return jsonify(channels)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
