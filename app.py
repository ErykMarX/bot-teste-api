from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = '7099713057:AAFZJlzCNXGhNA9_hWkuCI9UevoEG_YhRuc'
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
ARQUIVO_LOG = 'logs_testes_api.json'

usuarios = {}  # Armazena o progresso das perguntas por usuário

def salvar_log(dados):
    if os.path.exists(ARQUIVO_LOG):
        with open(ARQUIVO_LOG, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(dados)
    with open(ARQUIVO_LOG, 'w') as f:
        json.dump(logs, f, indent=2)

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

    if chat_id not in usuarios:
        usuarios[chat_id] = {"etapa": "inicial"}

    etapa = usuarios[chat_id]["etapa"]

    if texto.startswith("/testarapi"):
        usuarios[chat_id] = {"etapa": "client_id"}
        enviar(chat_id, "Informe o *client_id*:")

    elif etapa == "client_id":
        usuarios[chat_id]["client_id"] = texto.strip()
        usuarios[chat_id]["etapa"] = "client_secret"
        enviar(chat_id, "Informe o *client_secret*:")

    elif etapa == "client_secret":
        usuarios[chat_id]["client_secret"] = texto.strip()
        usuarios[chat_id]["etapa"] = "ip"
        enviar(chat_id, "Informe o *IP/base da API* (ex: https://192.168.0.1):")

    elif etapa == "ip":
        url_base = texto.strip()
        client_id = usuarios[chat_id]['client_id']
        client_secret = usuarios[chat_id]['client_secret']

        payload = {
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": "integrador@saperx.com.br",
            "password": "Meyewhfz7h5nUdsefD1Yasl3x3"
        }

        try:
            r = requests.post(f"{url_base}/oauth/token", json=payload, headers={"Content-Type": "application/json"}, verify=False)
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
        usuarios[chat_id]["etapa"] = "final"

    else:
        enviar(chat_id, "Envie /testarapi para iniciar o teste da API.")

    return "ok"

@app.route("/")
def index():
    return "Bot rodando com Webhook!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

