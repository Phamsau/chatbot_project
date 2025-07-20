import os
from dotenv import load_dotenv
from openai import OpenAI  # ✅ đúng cú pháp cho SDK mới

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def loc_lich_su(lich_su):
    """Lọc bỏ các câu trả lời xin lỗi không cần thiết để tránh lặp lại"""
    return [
        msg for msg in lich_su
        if not (
            msg['role'] == 'assistant' and
            msg['content'].strip().lower().startswith("xin lỗi")
        )
    ]


def lam_dep_cau_tra_loi_groq(cau_hoi, noi_dung_tham_khao, ngu_canh=None):

    ngu_canh = loc_lich_su(ngu_canh or [])

    # Xây messages với prompt rõ ràng, hạn chế xin lỗi
    messages = [
        {"role": "system", "content": (
            "Bạn là một trợ lý AI tiếng Việt đáng tin cậy. "
            "Chỉ trả lời dựa trên thông tin đã có. "
            "Không cần xin lỗi nếu không thực sự có lỗi."
        )}
    ] + ngu_canh

    if cau_hoi:
        messages.append({"role": "user", "content": cau_hoi})
    if noi_dung_tham_khao:
        messages.append({"role": "assistant", "content": noi_dung_tham_khao})

    # Yêu cầu làm rõ lại
    messages.append({
        "role": "user",
        "content": "Hãy viết lại câu trả lời mạch lạc, rõ ràng, thân thiện, chính xác thông tin tra cứu đươc, không bịa chuyện. Không lặp lại xin lỗi nhiều lần."
    })

    try:
        ket_qua = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,  # Tăng chút để văn phong tự nhiên
            max_tokens=300
        )
        return ket_qua.choices[0].message.content.strip()
    except Exception as e:
        return f"[Lỗi từ Groq] {e}"
