import os
from dotenv import load_dotenv
from openai import OpenAI  # ✅ đúng cú pháp cho SDK mới

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def lam_dep_cau_tra_loi_groq(cau_hoi, cau_tra_loi_goc, ngu_canh=None):
    ngu_canh = ngu_canh or []
    messages = [
        {"role": "system", "content": "Bạn là một trợ lý AI tiếng Việt đáng tin cậy. Chỉ trả lời dựa trên thông tin đã có. Nếu không biết, hãy nói 'Tôi không có đủ thông tin.'"}
    ] + ngu_canh + [
        {"role": "user", "content": cau_hoi}
    ]

    if cau_tra_loi_goc:
        messages.append({"role": "assistant", "content": cau_tra_loi_goc})

    messages.append({
        "role": "user",
        "content": "→ Viết lại câu trả lời bằng tiếng Việt mạch lạc và thân thiện. Tuyệt đối không bịa đặt!"
    })

    try:
        ket_qua = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        return ket_qua.choices[0].message.content.strip()
    except Exception as e:
        return f"[Lỗi từ Groq] {e}"
