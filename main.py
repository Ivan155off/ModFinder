from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModFinder | Minecraft Search</title>
    <style>
        :root { --red: #ff0000; --bg: #080808; --card: #121212; }
        body { 
            background: var(--bg); color: white; font-family: 'Inter', sans-serif;
            display: flex; flex-direction: column; align-items: center; padding: 40px; margin: 0;
        }
        .container {
            width: 100%; max-width: 600px; background: var(--card); border: 2px solid var(--red);
            border-radius: 25px; padding: 30px; box-shadow: 0 0 30px rgba(255,0,0,0.2); text-align: center;
        }
        h1 { color: var(--red); letter-spacing: 8px; font-size: 2.5em; margin-bottom: 20px; text-transform: uppercase; }
        .search-bar { display: flex; gap: 10px; margin-bottom: 20px; }
        input, select {
            padding: 12px; background: #000; border: 1px solid #333; color: white; border-radius: 10px; outline: none;
        }
        input { flex-grow: 2; }
        .btn {
            background: var(--red); color: white; border: none; padding: 15px;
            border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; text-transform: uppercase;
        }
        .btn:hover { background: #cc0000; transform: scale(1.01); }
        #results { margin-top: 30px; width: 100%; max-width: 600px; display: grid; gap: 15px; }
        .mod-card {
            background: #181818; border: 1px solid #222; border-radius: 15px; padding: 15px;
            display: flex; align-items: center; gap: 15px; animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .mod-card img { width: 60px; height: 60px; border-radius: 10px; }
        .mod-info { flex-grow: 1; text-align: left; }
        .mod-name { font-weight: bold; color: var(--red); display: block; }
        .mod-desc { font-size: 13px; color: #888; margin-top: 4px; }
        .get-btn {
            background: #333; color: white; text-decoration: none; padding: 8px 12px;
            border-radius: 8px; font-size: 12px; font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ModFinder</h1>
        <div class="search-bar">
            <input type="text" id="q" placeholder="What mod are you looking for?">
            <select id="v">
                <option value="">All Ver.</option>
                <option value="1.20.1">1.20.1</option>
                <option value="1.19.2">1.19.2</option>
                <option value="1.18.2">1.18.2</option>
                <option value="1.16.5">1.16.5</option>
                <option value="1.12.2">1.12.2</option>
                <option value="1.7.10">1.7.10</option>
            </select>
        </div>
        <button class="btn" onclick="runSearch()">Search Now</button>
    </div>
    <div id="results"></div>

    <script>
        async function runSearch() {
            const q = document.getElementById('q').value;
            const v = document.getElementById('v').value;
            const res = document.getElementById('results');
            if(!q) return;
            res.innerHTML = '<p>Searching...</p>';
            try {
                const r = await fetch(`/api/search?q=${encodeURIComponent(q)}&v=${v}`);
                const mods = await r.json();
                res.innerHTML = '';
                mods.forEach(m => {
                    res.innerHTML += `
                        <div class="mod-card">
                            <img src="${m.logo || 'https://via.placeholder.com/60'}" alt="icon">
                            <div class="mod-info">
                                <span class="mod-name">${m.name}</span>
                                <span class="mod-desc">${m.summary}</span>
                            </div>
                            <a href="${m.url}" target="_blank" class="get-btn">VIEW</a>
                        </div>
                    `;
                });
            } catch(e) { res.innerHTML = '<p>Error loading mods.</p>'; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    ver = request.args.get('v', '')
    url = f"https://www.curseforge.com/api/v1/mods/search?gameId=432&searchFilter={query}&gameVersion={ver}&index=0&pageSize=10&sortField=1"
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = r.json()
        mods = []
        for m in data.get('data', []):
            mods.append({
                "name": m.get('name'),
                "summary": m.get('summary'),
                "logo": m.get('logo', {}).get('thumbnailUrl'),
                "url": f"https://www.curseforge.com/minecraft/mc-mods/{m.get('slug')}"
            })
        return jsonify(mods)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run()
