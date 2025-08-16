
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
            "Bạn là một trợ lý AI tiếng Việt đáng tin cậy và vui vẻ."
            "Câu trả lời phải luôn bằng tiếng Việt, nếu gặp đoạn tiếng Anh thì phải dịch ra tiếng Việt."
            "Nếu gặp câu hỏi dạng: ai tạo ra bạn, bạn là ai ... thì trả lời: 'Tôi là do ông Phạm Sáu tạo ra, sử dụng nguồn dữ liệu nội bộ, nguồn từ seach Google và tích hợp mô hình ngôn ngữ LLama để trả lời...'."
            "Nếu hỏi về ông Phạm Sáu là ai, thì trả lời: 'Ông ấy là một kỹ sư xây dựng già...', có thể thêm hài hước 1 tí."
            "Không bịa chuyện và không xin lỗi khi không cần thiết."
        )}
    ] + ngu_canh

    if cau_hoi:
        messages.append({"role": "user", "content": cau_hoi})
    if noi_dung_tham_khao:
        messages.append({"role": "assistant", "content": noi_dung_tham_khao})
    print(messages)
    messages.append({
        "role": "user",
        "content": (
            "Viết lại câu trả lời mạch lạc, rõ ràng, thân thiện, chính xác và phải trích nguồn nếu có"
            "yêu cầu: dựa vào content từ user và assistant để trả lời."
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

        return content

    except Exception as e:
        return f"[Lỗi từ Groq] {e}", []


def lam_sach_van_ban(text: str) -> str:
    """Xử lý bỏ dấu ngoặc kép, ký tự đặc biệt, ký tự điều khiển, khoảng trắng thừa."""
    if not text:
        return ""
    text = re.sub(r"[\"'`]+", "", text)  # bỏ dấu ngoặc kép, backtick
    text = re.sub(r"[\x00-\x1F\x7F]", "", text)  # bỏ ký tự điều khiển ASCII
    text = re.sub(r"[★♦•■◆✓✔✗❌✅]", "", text)  # bỏ ký hiệu lạ
    text = re.sub(r"\s+", " ", text).strip()  # xóa khoảng trắng thừa
    text = text.strip(" ,.:;!?()[]{}")  # bỏ dấu câu đầu/cuối
    return text


def tao_tu_khoa_google(cau_hoi: str, ngu_canh=None, model_name="llama3-8b-8192") -> dict:
    ngu_canh = ngu_canh or []

    try:
        # --- Bước 1: Kiểm tra liên quan ---
        context_text = " ".join(m.get("content", "")
                                for m in ngu_canh if isinstance(m, dict))

        check_res = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": (
                    "Bạn là công cụ xác định xem một câu hỏi có liên quan đến ngữ cảnh hay không."
                    "Ngữ cảnh có thể chứa thông tin về một nhân vật hoặc sự kiện."
                    "Câu hỏi được coi là liên quan nếu:"
                    "- Nhắc trực tiếp đến nhân vật hoặc sự kiện chính trong ngữ cảnh."
                    "- Hoặc hỏi về mối quan hệ, sự kiện, hoặc chi tiết có liên quan đến nhân vật/sự kiện chính."
                    "Nếu không liên quan thì trả 'NO'. Nếu liên quan thì trả 'YES'."
                    "Không giải thích, chỉ trả 'YES' hoặc 'NO'."
                )},
                {"role": "user", "content": f"Ngữ cảnh:\n{context_text}\n\nCâu hỏi:\n{cau_hoi}\n\nLiên quan không?"}
            ],
            temperature=0,
            max_tokens=3
        )

        is_related = (
            check_res.choices[0].message.content or "").strip().upper()
        related = (is_related == "YES")

        # --- Bước 2: Luôn tạo từ khóa ---
        res = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": (
                    "Bạn là công cụ tạo 1 cụm từ khóa tìm kiếm Google ngắn gọn, chính xác."
                    "Luôn trả về cụm từ khóa bằng tiếng Việt."
                    "Nếu câu hỏi không phải tiếng Việt, hãy dịch sang tiếng Việt rồi tạo từ khóa."
                    "Chỉ trả về cụm từ khóa, không giải thích."
                )},
                *ngu_canh,
                {"role": "user", "content": f"Chuyển câu hỏi '{cau_hoi}' thành 1 cụm từ khóa tiếng Việt"}
            ],
            temperature=0.2,
            max_tokens=20
        )

        raw = getattr(res.choices[0].message, "content", "") or ""
        tu_khoa = lam_sach_van_ban(raw.split("\n")[0])

        return {"success": related, "keyword": tu_khoa, "error": None}

    except Exception as e:
        return {"success": False, "keyword": None, "error": str(e)}
