# estrutura de arquivos:
# bot_teste_api_webhook/
# ├── app.py
# ├── requirements.txt
# ├── Procfile
# └── logs_testes_api.json (será criado automaticamente)

from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = '7099713057:AAFZJlzCNXGhNA9_hWkuCI9UevoEG_YhRuc'
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
USERNAME = 'integrador@saperx.com.br'
PASSWORD = 'Meyewhfz7h5nUdsefD1Yas1sx3'

ARQUIVO_LOG = 'logs_testes_api.json'

# Salva os testes realizados em um JSON
def salvar_log(dados):
    if os.path.exists(ARQUIVO_LOG):
        with open(ARQUIVO_LOG, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(dados)
    with open(ARQUIVO_LOG, 'w') as f:
        json.dump(logs, f, indent=2)

# Envia mensagem para o Telegram
def enviar(chat_id, texto):
    requests.post(f"{API_URL}/sendMessage", data={
        'chat_id': chat_id,
        'text': texto
    })

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    msg = update.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    texto = msg.get("text", "")

    if texto.startswith("/testarapi"):
        enviar(chat_id, "🔍 Me envie a URL base da API (ex: https://api.exemplo.com):")
    elif texto.startswith("http"):
        url_base = texto.strip()
        client_id = "API_KEY_EXEMPLO"
        client_secret = "API_SECRET_EXEMPLO"

        payload = {
            'grant_type': 'password',
            'username': USERNAME,
            'password': PASSWORD,
            'client_id': client_id,
            'client_secret': client_secret
        }
        try:
            r = requests.post(f"{url_base}/oauth/token", data=payload, timeout=10)
            status = r.status_code
            conteudo = r.json() if status == 200 else r.text
            salvar_log({
                "data": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "usuario": msg.get("from", {}).get("first_name", "desconhecido"),
                "url": url_base,
                "status": status,
                "resposta": conteudo
            })
            resposta = f"✅ Status {status}\n{conteudo}" if status == 200 else f"❌ Erro {status}\n{conteudo}"
        except Exception as e:
            resposta = f"❌ Falha na requisição:\n{e}"
        enviar(chat_id, resposta)
    else:
        enviar(chat_id, "Envie /testarapi para iniciar ou envie a URL da API diretamente.")

    return "ok"

@app.route("/")
def index():
    return "Bot rodando com Webhook!", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

