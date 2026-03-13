from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "PPT Assistant Server Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # 飞书验证 challenge
    if "challenge" in data:
        return jsonify({
            "challenge": data["challenge"]
        })

    print("收到飞书消息:", data)

    return jsonify({
        "status": "ok"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
