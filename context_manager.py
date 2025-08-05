import time

GLOBAL_CONTEXTS = {}
SESSION_TIMEOUT = 600  # 10 phút


def get_user_context(user_id):
    now = time.time()
    ctx = GLOBAL_CONTEXTS.get(user_id)
    if ctx and (now - ctx["last_active"]) < SESSION_TIMEOUT:
        return ctx["context"]

    # Tạo ngữ cảnh mới nếu không tồn tại hoặc hết hạn
    GLOBAL_CONTEXTS[user_id] = {
        "context": {
            "history": [],
            "danh_tu_rieng_truoc_do": None,
            "tiep": "",
            "dk": False,
            "current_position": 0
        },
        "last_active": now
    }
    return GLOBAL_CONTEXTS[user_id]["context"]


def update_user_context(user_id, context_data):
    GLOBAL_CONTEXTS[user_id] = {
        "context": context_data,
        "last_active": time.time()
    }


def cleanup_old_contexts():
    now = time.time()
    expired = [uid for uid, v in GLOBAL_CONTEXTS.items() if now -
               v["last_active"] > SESSION_TIMEOUT]
    for uid in expired:
        del GLOBAL_CONTEXTS[uid]
