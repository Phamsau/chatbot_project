from flow_control import execute_command
from module_ggl import (
    luu_ngu_canh,
    search_google,
    xoa_ngucanh, xuli_doanvan_ngu_canh, tra_loi_tho
)
from module_xuli import hien_thi_vien_va_con_tro
from nghe_noi import recognize_speech1, speak_text1, speak_text
from datetime import datetime
from core.handle_input import sau, bay, tu_dien, ghi_dulieu_txt
from core.logic import tieptuc_traloi, tach_tu_khoa, capnhat
from ngu_canh_truy_van import tao_truy_van_bo_sung
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

        # Khởi tạo context nếu chưa có
        if "history" not in user_context:
            user_context["history"] = []
        if "danh_tu_rieng_truoc_do" not in user_context:
            user_context["danh_tu_rieng_truoc_do"] = None

        # Xóa ngữ cảnh
        if user_input == "xóa ngữ cảnh":
            xoa_ngucanh()
            user_context["history"] = []
            user_context["danh_tu_rieng_truoc_do"] = None
            return "Ngữ cảnh đã được xóa."

        # Tiếp tục đoạn văn nếu có
        if user_input == "tiếp tục" and user_context.get("dk"):
            tiep = user_context.get("tiep")
            current_position = user_context.get("current_position", 0)
            if tiep:
                next_words = tieptuc_traloi(tiep, current_position)
                return next_words if next_words else "Đã hết văn bản."
            else:
                return "Không có văn bản để trích xuất."

        # Xử lý từ ngữ cảnh cũ
        text, nguon = xuli_doanvan_ngu_canh(user_input)
        if text:
            user_response = tra_loi_tho(user_input, text)
            chatgpt_output, updated_history, danh_tu_rieng_moi = capnhat(
                user_input, user_response, user_context["history"], nguon)
            user_context["history"] = updated_history[-20:]
            if danh_tu_rieng_moi:
                user_context["danh_tu_rieng_truoc_do"] = danh_tu_rieng_moi[-1]
            return chatgpt_output

        # Từ điển nội bộ
        ct1 = sau(user_input)
        ct2 = bay(user_input)

        if ct1 and ct2:
            output = tu_dien.get(ct1)
            luu_ngu_canh(user_input, output)
            chatgpt_output, updated_history, danh_tu_rieng_moi = capnhat(
                user_input, output, user_context["history"])
            user_context["history"] = updated_history[-20:]
            if danh_tu_rieng_moi:
                user_context["danh_tu_rieng_truoc_do"] = danh_tu_rieng_moi[-1]
            return chatgpt_output

        # Một số câu hỏi đơn giản
        if ct1 in danh_muc():
            if ct1 == "ngày mấy":
                return f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
            elif ct1 == "mấy giờ rồi":
                return f"Bây giờ là {datetime.now().strftime('%H:%M')}"
            return tu_dien.get(ct1)

        # Cuối cùng, truy vấn Google
        truy_van = tao_truy_van_bo_sung(
            user_input, user_context["danh_tu_rieng_truoc_do"])
        user_response, tiep, nguon = search_google(truy_van, user_input)
        user_context["tiep"] = tiep
        user_context["dk"] = True
        user_context["current_position"] = len(user_response.split())

        chatgpt_output, updated_history, danh_tu_rieng_moi = capnhat(
            user_input, user_response, user_context["history"], nguon)
        user_context["history"] = updated_history[-20:]
        if danh_tu_rieng_moi:
            user_context["danh_tu_rieng_truoc_do"] = danh_tu_rieng_moi[-1]
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
    danh_tu_rieng_truoc_do = []

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
                danh_tu_rieng_truoc_do = []

            elif user_input == "":
                chatgpt_output = "Xin vui lòng cho biết yêu cầu của bạn"

            else:
                dk = False
                user_input = user_input.lower().strip()
                text, nguon = xuli_doanvan_ngu_canh(user_input)
                best_related_answer = None
                print(nguon)

                if text:
                    best_related_answer = tra_loi_tho(
                        user_input, text)

                if best_related_answer:
                    # print(
                    # "kết quả trả lời sau khi tra ngữ cảnh qua hàm tra_loi_tho file main(): ", best_related_answer)
                    chatgpt_output, updated_history, danh_tu_rieng_moi = capnhat(
                        user_input, best_related_answer, history, nguon)
                    history = updated_history[-20:]
                    danh_tu_rieng_truoc_do = danh_tu_rieng_moi[-1] if danh_tu_rieng_moi else None
                else:
                    ct1 = sau(user_input)
                    ct2 = bay(user_input)
                    print(ct1, ct2)

                    if ct1 and ct2 and ct1 in tu_dien and ct1 in ct2:
                        chatgpt_output, updated_history, danh_tu_rieng_moi = capnhat(
                            user_input, tu_dien[ct1], history)
                        history = updated_history[-20:]
                        danh_tu_rieng_truoc_do = danh_tu_rieng_moi[-1] if danh_tu_rieng_moi else None
                        luu_ngu_canh(user_input, chatgpt_output)

                    elif ct1 in danh_muc() and not ct2:
                        if ct1 == "ngày mấy":
                            chatgpt_output = f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
                        elif ct1 == "mấy giờ rồi":
                            chatgpt_output = f"Bây giờ là {datetime.now().strftime('%H:%M')}"
                        else:
                            chatgpt_output = tu_dien.get(ct1)

                    else:
                        truy_van = tao_truy_van_bo_sung(
                            user_input, danh_tu_rieng_truoc_do)
                        user_response, tiep, nguon = search_google(
                            truy_van, user_input)

                        dk = True
                        current_position = len(user_response.split())
                        chatgpt_output, updated_history, danh_tu_rieng_moi = capnhat(
                            user_input, user_response, history, nguon)
                        history = updated_history[-20:]
                        danh_tu_rieng_truoc_do = danh_tu_rieng_moi[-1] if danh_tu_rieng_moi else None

                        # 🔁 Lưu dữ liệu vào file .txt nếu là từ Google
                        # ghi_dulieu_txt(user_input, chatgpt_output)
            print(
                "kết quả test thử user_input với hàm lay_tham_chieu_theo_dai_tu: ", danh_tu_rieng_truoc_do)
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
