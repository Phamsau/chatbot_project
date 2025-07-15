import os
from dotenv import load_dotenv
from openai import OpenAI  # đúng chuẩn mới

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def lam_dep_cau_tra_loi_groq(user_input, raw_answer, history=None):
    history = history or []
    history += [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": raw_answer},
        {"role": "user", "content": "→ Viết lại câu trả lời bằng tiếng Việt mạch lạc và thân thiện."}
    ]
    try:
        resp = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=history,
            temperature=0.7,
            max_tokens=300
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Lỗi từ Groq] {e}"
