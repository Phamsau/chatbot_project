from flask import Flask, request, jsonify, render_template
from main import chatbot_response

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        reply = chatbot_response(user_input)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Lỗi xử lý: {str(e)}"})


if __name__ == "__main__":
    import os
    # 10000 là fallback cho chạy local
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
