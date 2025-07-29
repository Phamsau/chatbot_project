import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def lam_dep_cau_tra_loi_groq(cau_hoi, noi_dung_tham_khao, ngu_canh=None):
    def loc_lich_su(lich_su):
        return [
            msg for msg in lich_su
            if not (
                msg['role'] == 'assistant' and
                msg['content'].strip().lower().startswith("xin lỗi")
            )
        ]

    ngu_canh = loc_lich_su(ngu_canh or [])

    messages = [
        {"role": "system", "content": (
            "Bạn là một trợ lý AI tiếng Việt đáng tin cậy. "
            "Chỉ trả lời dựa trên thông tin có thật. "
            "Không bịa chuyện và không xin lỗi khi không cần thiết."
        )}
    ] + ngu_canh

    if cau_hoi:
        messages.append({"role": "user", "content": cau_hoi})
    if noi_dung_tham_khao:
        messages.append({"role": "assistant", "content": noi_dung_tham_khao})

    messages.append({
        "role": "user",
        "content": (
            "Viết lại câu trả lời mạch lạc, rõ ràng, thân thiện, chính xác và phải trích nguồn nếu có"
            "yêu cầu: Tên nhân vật phải đủ thông tin mới nêu, không gán ghép, không được đoán hay bịa đặt tên nhân vật khi thông tin không rõ ràng. "
            "Cuối cùng, ghi rõ dòng sau:\n"
            "[DANH_TU_RIENG: tên đầy đủ hoặc chủ đề chính mà người dùng đang đề cập nếu có]"
        )
    })

    try:
        ket_qua = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=400
        )
        content = ket_qua.choices[0].message.content.strip()

        match = re.search(r"\[DANH_TU_RIENG:(.*?)\]\s*$", content, re.DOTALL)
        danh_tu_rieng = []
        if match:
            danh_tu_rieng = list(
                {ten.strip() for ten in match.group(1).split(",") if ten.strip()}
            )
            content = content[:match.start()].strip()

        return content, danh_tu_rieng

    except Exception as e:
        return f"[Lỗi từ Groq] {e}", []
