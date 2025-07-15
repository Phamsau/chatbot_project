# core/groq.py


import os
from dotenv import load_dotenv
from openai import OpenAI

# Load biến môi trường từ file .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key
)


def lam_dep_cau_tra_loi_groq(user_input, raw_answer, history=None):
    # Khởi tạo lịch sử nếu chưa có
    if history is None:
        history = []

    # Thêm câu hỏi và câu trả lời thô vào lịch sử
    history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": raw_answer}
    ]

    # Thêm yêu cầu "viết lại cho tự nhiên"
    history.append({
        "role": "user",
        "content": "→ Hãy viết lại câu trả lời bằng tiếng Việt Nam một cách mạch lạc, thân thiện."
    })

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=history,
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Lỗi từ Groq] {str(e)}"
