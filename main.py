from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModFinder | Minecraft</title>
    <style>
        :root { --red: #ff0000; --bg: #080808; --card: #121212; }
        body { 
            background: var(--bg); color: white; font-family: sans-serif;
            display: flex; flex-direction: column; align-items: center; padding: 20px;
        }
        .container {
            width: 100%; max-width: 600px; background: var(--card); border: 2px solid var(--red);
            border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 0 20px rgba(255,0,0,0.2);
        }
        h1 { color: var(--red); letter-spacing: 5px; text-transform: uppercase; }
        .form { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        input, select {
            padding: 12px; background: #000; border: 1px solid #333; color: white; border-radius: 10px; flex: 1; min-width: 150px;
        }
        .btn {
            background: var(--red); color: white; border: none; padding: 15px;
            border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%;
        }
        #results { margin-top: 20px; width: 100%; max-width: 600px; }
        .mod-card {
            background: #181818; border: 1px solid #222; border-radius: 15px; padding: 15px;
            display: flex; align-items: center; gap: 15px; margin-bottom: 10px;
        }
        .mod-card img { width: 50px; height: 50px; border-radius: 8px; }
        .mod-info { flex-grow: 1; text-align: left; }
        .mod-name { font-weight: bold; color: var(--red); }
        .mod-desc { font-size: 12px; color: #888; }
        .get-btn { background: #333; color: white; text-decoration: none; padding: 5px 10px; border-radius: 5px; font-size: 11px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ModFinder</h1>
        <div class="form">
            <input type="text" id="q" placeholder="Search mods (e.g. guns)">
            <select id="v">
                <option value="">All Versions</option>
                <option value="1.20.1">1.20.1</option>
                <option value="1.19.2">1.19.2</option>
                <option value="1.18.2">1.18.2</option>
                <option value="1.16.5">1.16.5</option>
                <option value="1.12.2">1.12.2</option>
            </select>
        </div>
        <button class="btn" onclick="doSearch()">SEARCH</button>
    </div>
    <div id="results"></div>

    <script>
        async function doSearch() {
            const q = document.getElementById('q').value;
            const v = document.getElementById('v').value;
            const res = document.getElementById('results');
            if(!q) return;
            
            res.innerHTML = '<p>Searching...</p>';
            
            try {
                // Прямой вызов нашего API
                const r = await fetch(`/search_api?q=${encodeURIComponent(q)}&v=${v}`);
                const data = await r.json();
                
                if (data.length === 0) {
                    res.innerHTML = '<p>No mods found or API error.</p>';
                    return;
                }

                res.innerHTML = '';
                data.forEach(m => {
                    res.innerHTML += `
                        <div class="mod-card">
                            <img src="${m.logo}" onerror="this.src='https://via.placeholder.com/50'">
                            <div class="mod-info">
                                <div class="mod-name">${m.name}</div>
                                <div class="mod-desc">${m.summary}</div>
                            </div>
                            <a href="${m.url}" target="_blank" class="get-btn">VIEW</a>
                        </div>
                    `;
                });
            } catch(e) {
                res.innerHTML = '<p>Error connecting to server.</p>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search_api')
def search_api():
    query = request.args.get('q', '')
    version = request.args.get('v', '')
    
    # Используем альтернативный эндпоинт CurseForge
    search_url = f"https://www.curseforge.com/api/v1/mods/search?gameId=432&searchFilter={query}&gameVersion={version}&index=0&pageSize=10&sortField=1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}") # Это будет видно в логах Render
        
        if response.status_code != 200:
            return jsonify([])
            
        data = response.json()
        mods = []
        for item in data.get('data', []):
            mods.append({
                "name": item.get('name'),
                "summary": item.get('summary', '')[:80] + '...',
                "logo": item.get('logo', {}).get('thumbnailUrl', ''),
                "url": f"https://www.curseforge.com/minecraft/mc-mods/{item.get('slug')}"
            })
        return jsonify(mods)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run()
