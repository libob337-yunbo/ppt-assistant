from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "PPT Assistant Server Running"

@app.route("/ppt_task", methods=["POST"])
def ppt_task():
    data = request.json
    instruction = data.get("instruction")

    result = f"PPT任务已收到: {instruction}"

    return jsonify({
        "status": "success",
        "result": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
