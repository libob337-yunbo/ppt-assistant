from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET")

print("APP_ID:", FEISHU_APP_ID)
print("APP_SECRET:", FEISHU_APP_SECRET)
def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url,json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    })
    return res.json()["tenant_access_token"]

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    event = data.get("event", {})
    message = event.get("message", {})
    chat_id = message.get("chat_id")

    token = get_tenant_token()

    url = "https://open.feishu.cn/open-apis/im/v1/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": "{\"text\":\"你好，我是PPT助手 🤖\"}"
    }

    requests.post(url, headers=headers, json=body, params={"receive_id_type":"chat_id"})

    return "ok"

@app.route("/")
def home():
    return "PPT Assistant Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
