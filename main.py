from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Инициализация клиента OpenAI (ключ возьмем из настроек Render)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Moduino AI | Powered by OpenAI</title>
    <style>
        :root { --red: #ff0000; --bg: #050505; }
        body { background: var(--bg); color: white; font-family: 'Courier New', monospace; padding: 40px; display: flex; flex-direction: column; align-items: center; }
        .container { width: 100%; max-width: 800px; background: #111; border: 2px solid var(--red); border-radius: 20px; padding: 30px; box-shadow: 0 0 30px rgba(255,0,0,0.2); }
        h1 { color: var(--red); text-align: center; letter-spacing: 5px; }
        textarea { width: 100%; height: 100px; background: #000; border: 1px solid #333; color: white; padding: 15px; border-radius: 10px; font-size: 16px; margin-bottom: 20px; resize: none; }
        .btn { width: 100%; background: var(--red); color: white; border: none; padding: 15px; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 18px; }
        pre { background: #000; padding: 20px; border-radius: 10px; border: 1px solid #222; color: #0f0; overflow-x: auto; margin-top: 20px; white-space: pre-wrap; min-height: 200px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MODUINO AI</h1>
        <p style="text-align:center; color:#888;">Опиши любые компоненты (хоть миллиард), и ИИ напишет код</p>
        <textarea id="prompt" placeholder="Например: Arduino Nano, датчик DHT11 на 2 пине, LCD 16x2 и сервопривод на 9 пине..."></textarea>
        <button class="btn" onclick="generateCode()">СГЕНЕРИРОВАТЬ КОД</button>
        <pre id="output">// Твой код появится здесь...</pre>
    </div>

    <script>
        async function generateCode() {
            const prompt = document.getElementById('prompt').value;
            const output = document.getElementById('output');
            if(!prompt) return;
            
            output.innerText = "Нейросеть думает... Подожди немного...";
            
            try {
                const response = await fetch('/ai_gen', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                output.innerText = data.code;
            } catch(e) {
                output.innerText = "Ошибка! Проверь API ключ в настройках Render.";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ai_gen', methods=['POST'])
def ai_gen():
    user_prompt = request.json.get('prompt')
    
    try {
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Или "gpt-4" если есть доступ
            messages=[
                {"role": "system", "content": "Ты эксперт по Arduino. Пиши только готовый C++ код с комментариями на русском. Не пиши лишних слов, только код."},
                {"role": "user", "content": f"Напиши код Arduino для следующей задачи: {user_prompt}"}
            ]
        )
        ai_code = response.choices[0].message.content
        return jsonify({"code": ai_code})
    except Exception as e:
        return jsonify({"code": f"Ошибка API: {str(e)}"})

if __name__ == '__main__':
    app.run()
