from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET")

print("APP_ID:", FEISHU_APP_ID)
print("APP_SECRET:", FEISHU_APP_SECRET)


def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    
    res = requests.post(url, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    })
    
    data = res.json()
    print("TOKEN RESPONSE:", data)
    
    if data.get("code") != 0:
        print("ERROR getting token:", data.get("msg"))
        return None
    
    return data.get("tenant_access_token")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("=" * 50)
    print("RECEIVED WEBHOOK:", json.dumps(data, ensure_ascii=False, indent=2))
    print("=" * 50)
    
    # 处理飞书验证请求
    if "challenge" in data:
        print("Challenge received:", data["challenge"])
        return jsonify({"challenge": data["challenge"]})
    
    # 获取事件信息
    event = data.get("event", {})
    message = event.get("message", {})
    
    # 获取消息类型和ID
    chat_type = message.get("chat_type")  # "p2p" 私聊 或 "group" 群聊
    chat_id = message.get("chat_id")
    sender = message.get("sender", {})
    sender_id = sender.get("sender_id", {}).get("open_id")
    
    print(f"Chat type: {chat_type}")
    print(f"Chat ID: {chat_id}")
    print(f"Sender ID: {sender_id}")
    
    # 获取用户发送的消息内容
    content_str = message.get("content", "{}")
    try:
        content = json.loads(content_str)
        user_text = content.get("text", "")
    except:
        user_text = ""
    print(f"User message: {user_text}")
    
    # 获取访问令牌
    token = get_tenant_token()
    if not token:
        print("ERROR: Failed to get tenant token")
        return jsonify({"code": 0}), 200
    
    # 发送回复消息
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 判断回复对象：私聊回复用户，群聊回复到群里
    if chat_type == "p2p":
        receive_id = sender_id
        receive_id_type = "open_id"
    else:
        receive_id = chat_id
        receive_id_type = "chat_id"
    
    print(f"Replying to: {receive_id} (type: {receive_id_type})")
    
    # 构建回复内容
    reply_text = f"你好，我是PPT助手 🤖\n\n你发送了：{user_text}\n\n请告诉我你需要什么主题的PPT？"
    
    body = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": reply_text}, ensure_ascii=False)
    }
    
    print("Sending message...")
    res = requests.post(
        url, 
        headers=headers, 
        json=body, 
        params={"receive_id_type": receive_id_type}
    )
    
    result = res.json()
    print("SEND MESSAGE RESULT:", json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("code") == 0:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Failed to send message: {result.get('msg')}")
    
    return jsonify({"code": 0}), 200


@app.route("/")
def home():
    return "PPT Assistant is running! 🚀"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
