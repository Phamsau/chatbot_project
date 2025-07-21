from flow_control import execute_command
from module_ggl import (
    luu_ngu_canh,
    search_google,
    xoa_ngucanh, xuli_doanvan_ngu_canh, tra_loi_tho
)
from module_xuli import hien_thi_vien_va_con_tro
from nghe_noi import recognize_speech1, speak_text1, speak_text
import pandas as pd
from datetime import datetime
from core.handle_input import sau, bay, tu_dien, ghi_dulieu_txt
from core.logic import tieptuc_traloi, tach_tu_khoa, capnhat
# Trạng thái phiên trò chuyện (session đơn giản trong bộ nhớ)
user_context = {
    "tiep": None,
    "current_position": 99,
    "dk": False,
    "previous_answers": luu_ngu_canh("question", "answer")
}


user_context = {}


def chatbot_response(user_input):
    try:
        user_input = user_input.lower().strip()
        if not user_input:
            return "Xin vui lòng cho biết yêu cầu của bạn"

        if "history" not in user_context:
            user_context["history"] = []

        if user_input == "xóa ngữ cảnh":
            xoa_ngucanh()
            user_context["history"] = []
            return "Ngữ cảnh đã được xóa."

        if user_input == "tiếp tục" and user_context.get("dk"):
            tiep = user_context.get("tiep")
            current_position = user_context.get("current_position", 0)
            if tiep:
                next_words = tieptuc_traloi(tiep, current_position)
                return next_words if next_words else "Đã hết văn bản."
            else:
                return "Không có văn bản để trích xuất."

        # Tra trong ngữ cảnh trước
        text = xuli_doanvan_ngu_canh(user_input)
        if text:
            user_response = tra_loi_tho(user_input, text)
            chatgpt_output, updated_history = capnhat(
                user_input, user_response, user_context["history"])
            user_context["history"] = updated_history[-20:]
            return chatgpt_output

        # Tra theo từ điển nội bộ
        ct1 = sau(user_input)
        ct2 = bay(user_input)

        if ct1 and ct2:
            output = tu_dien.get(ct1)
            luu_ngu_canh(user_input, output)
            chatgpt_output, updated_history = capnhat(
                user_input, output, user_context["history"])
            user_context["history"] = updated_history[-20:]
            return chatgpt_output

        if ct1 in danh_muc():
            if ct1 == "ngày mấy":
                return f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
            elif ct1 == "mấy giờ rồi":
                return f"Bây giờ là {datetime.now().strftime('%H:%M')}"
            return tu_dien.get(ct1)

        # Cuối cùng: tra Google
        user_response, tiep = search_google(user_input)
        user_context["tiep"] = tiep
        user_context["dk"] = True
        user_context["current_position"] = len(user_response.split())

        chatgpt_output, updated_history = capnhat(
            user_input, user_response, user_context["history"])
        user_context["history"] = updated_history[-20:]

        # Ghi dữ liệu mới vào file
        # ghi_dulieu_txt(user_input, chatgpt_output)

        return chatgpt_output

    except Exception as e:
        return f"Lỗi: {str(e)}"


def danh_muc():
    return [
        "ngày mấy", "mấy giờ rồi", "đặt phòng", "thời tiết", "danh từ",
        "tính từ", "động từ", "xem ảnh", "thông dịch", "phiên dịch"
    ]


def main():
    list_cmd = [
        "Ok, Tôi sẵn sàng, xin bạn chờ trong giây lát",
        "Ok, mời bạn nghe thông tin thời tiết của chúng tôi",
        "Ok, mời bạn bắt đầu đăng ký đặt phòng.",
        "Ok, xin cho biết bạn trả phòng số mấy?",
        "OK Mời bạn xem hình em Ngọc Trinh",
        "Đã xem ảnh"
    ]

    dk = False
    cv = True
    no_speech_count = 0
    tiep = ""
    history = []

    try:
        speak_text("Xin chào, tôi giúp được gì cho bạn?")
        xoa_ngucanh()

        while True:
            if cv:
                user_input = input("User: ")
            else:
                user_input = recognize_speech1().strip().replace('\n', '')

            if user_input.lower() == "ok" or no_speech_count >= 2:
                speak_text("Chương trình đã thoát")
                break

            elif user_input.lower() == "thay đổi":
                cv = not cv
                chatgpt_output = "mời bạn tiếp tục trò chuyện"

            elif user_input.lower() == "tiếp tục" and dk:
                if tiep:
                    next_words = tieptuc_traloi(tiep, current_position)
                    chatgpt_output = next_words or "Đã hết văn bản."
                    dk = bool(next_words)
                else:
                    chatgpt_output = "Không có văn bản để trích xuất."

            elif user_input.lower() == "xóa ngữ cảnh":
                chatgpt_output = "Ok, Ngữ cảnh cuộc trò chuyện đã xóa"
                xoa_ngucanh()
                history = []

            elif user_input == "":
                chatgpt_output = "Xin vui lòng cho biết yêu cầu của bạn"

            else:
                dk = False
                user_input = user_input.lower().strip()
                text = xuli_doanvan_ngu_canh(user_input)
                best_related_answer = None

                if text:
                    best_related_answer = tra_loi_tho(user_input, text)

                if best_related_answer:
                    chatgpt_output, updated_history = capnhat(
                        user_input, best_related_answer, history)
                    history = updated_history[-20:]

                else:
                    ct1 = sau(user_input)
                    ct2 = bay(user_input)
                    print(ct1, ct2)

                    if ct1 and ct2 and ct1 in tu_dien and ct1 in ct2:
                        chatgpt_output, updated_history = capnhat(
                            user_input, tu_dien[ct1], history)
                        history = updated_history[-20:]
                        luu_ngu_canh(user_input, chatgpt_output)

                    elif ct1 in danh_muc() and not ct2:
                        if ct1 == "ngày mấy":
                            chatgpt_output = f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
                        elif ct1 == "mấy giờ rồi":
                            chatgpt_output = f"Bây giờ là {datetime.now().strftime('%H:%M')}"
                        else:
                            chatgpt_output = tu_dien.get(ct1)

                    else:
                        user_response, tiep = search_google(user_input)
                        dk = True
                        current_position = len(user_response.split())
                        chatgpt_output, updated_history = capnhat(
                            user_input, user_response, history)
                        history = updated_history[-20:]

                        # 🔁 Lưu dữ liệu vào file .txt nếu là từ Google
                        # ghi_dulieu_txt(user_input, chatgpt_output)

            hien_thi_vien_va_con_tro(chatgpt_output)

            if not cv:
                speak_text1(chatgpt_output)

            if chatgpt_output == "hôm nay là ngày":
                speak_text(datetime.now().strftime("%d/%m/%Y"))

            if chatgpt_output == "hiện tại là":
                speak_text(datetime.now().strftime("%H:%M"))

            if chatgpt_output in list_cmd:
                execute_command(chatgpt_output)

            if user_input == "":
                no_speech_count += 1
            else:
                no_speech_count = 0

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")


if __name__ == "__main__":
    main()
