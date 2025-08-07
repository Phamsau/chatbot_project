from core.logic import tieptuc_traloi, capnhat
from core.handle_input import sau, bay, tu_dien
from module_ggl import (
    luu_ngu_canh,
    search_google,
    xoa_ngucanh, xuli_doanvan_ngu_canh, tra_loi_tho
)
from datetime import datetime
from core.handle_input import sau, bay, tu_dien, ghi_dulieu_txt
from core.logic import tieptuc_traloi, tach_tu_khoa, capnhat
from ngu_canh_truy_van import tao_truy_van_bo_sung
# Trạng thái phiên trò chuyện (session đơn giản trong bộ nhớ)


def danh_muc():
    return [
        "ngày mấy", "mấy giờ rồi", "đặt phòng", "thời tiết", "danh từ",
        "tính từ", "động từ", "xem ảnh", "thông dịch", "phiên dịch"
    ]


def chatbot_response(user_input, user_context):
    try:
        user_input = user_input.lower().strip()
        if not user_input:
            xoa_ngucanh(user_context)
            user_context.update({
                "history": [],
                "danh_tu_rieng_truoc_do": None,
                "tiep": "",
                "dk": False,
                "current_position": 0,
                "previous_answers": {}
            })
            return "Xin chào! Tôi là trợ lý P.SAUAI, xin vui lòng cho biết yêu cầu của bạn."

        if user_input == "xóa ngữ cảnh":
            xoa_ngucanh(user_context)
            user_context["history"].clear()
            user_context["danh_tu_rieng_truoc_do"] = None
            return "Ngữ cảnh đã được xóa."

        if user_input == "tiếp tục" and user_context.get("dk"):
            tiep = user_context.get("tiep")
            pos = user_context.get("current_position", 0)
            if tiep:
                next_words = tieptuc_traloi(tiep, pos)
                return next_words or "Đã hết văn bản."
            return "Không có văn bản để trích xuất."

        # Xử lý ngữ cảnh nếu có
        text, nguon = xuli_doanvan_ngu_canh(user_context, user_input)
        if text:
            user_response = tra_loi_tho(user_input, text)
            if user_response:
                chatgpt_output, updated_history, danh_tu_moi = capnhat(
                    user_input, user_response, user_context["history"], nguon
                )
                user_context["history"] = updated_history[-10:]
                if danh_tu_moi:
                    user_context["danh_tu_rieng_truoc_do"] = danh_tu_moi[-1]
                return chatgpt_output

        # Kiểm tra từ điển nội bộ
        ct1, nguon = sau(user_input)
        ct2 = bay(user_input)

        if ct1 and ct2:
            output = tu_dien.get(ct1)
            luu_ngu_canh(user_input, output, nguon, context=user_context)
            chatgpt_output, updated_history, danh_tu_moi = capnhat(
                user_input, output, user_context["history"], nguon
            )
            user_context["history"] = updated_history[-10:]
            if danh_tu_moi:
                user_context["danh_tu_rieng_truoc_do"] = danh_tu_moi[-1]
            return chatgpt_output

        elif ct1 in danh_muc():
            if ct1 == "ngày mấy":
                return f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
            elif ct1 == "mấy giờ rồi":
                return f"Bây giờ là {datetime.now().strftime('%H:%M')}"
            return tu_dien.get(ct1)

        # Truy vấn Google nếu không có trong từ điển
        truy_van = tao_truy_van_bo_sung(
            user_input, user_context["danh_tu_rieng_truoc_do"])
        user_response, tiep, nguon = search_google(
            truy_van, user_input, user_context)

        user_context["tiep"] = tiep
        user_context["dk"] = True
        user_context["current_position"] = len(user_response.split())

        chatgpt_output, updated_history, danh_tu_moi = capnhat(
            user_input, user_response, user_context["history"], nguon
        )
        user_context["history"] = updated_history[-10:]
        if danh_tu_moi:
            user_context["danh_tu_rieng_truoc_do"] = danh_tu_moi[-1]

        return chatgpt_output
    except Exception as e:
        return f"Lỗi: {str(e)}"
