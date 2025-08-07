from flask import Flask, request, jsonify, render_template
from main import chatbot_response
from context_manager import get_user_context, update_user_context, cleanup_old_contexts

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")  # Giao diện bạn tự thiết kế


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    # Ưu tiên client gửi user_id
    user_id = data.get("user_id") or request.remote_addr
    message = data.get("message", "")

    # Xử lý context
    cleanup_old_contexts()
    context = get_user_context(user_id)
    reply = chatbot_response(message, context)
    update_user_context(user_id, context)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
