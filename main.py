from flow_control import execute_command
from module_ggl import (
    luu_ngu_canh,
    search_google_1,
    xoa_ngucanh, xuli_doanvan_ngu_canh,
    traloi_theo_ngucanh2,
    traloi_theo_ngucanh1
)
from module_xuli import hien_thi_vien_va_con_tro
from nghe_noi import recognize_speech1, speak_text1, speak_text
import subprocess
import pandas as pd
from datetime import datetime
from core.handle_input import sau, bay, tu_dien
from core.logic import tieptuc_traloi, tach_tu_khoa, capnhat
# Trạng thái phiên trò chuyện (session đơn giản trong bộ nhớ)
user_context = {
    "tiep": None,
    "current_position": 99,
    "dk": False,
    "previous_answers": luu_ngu_canh("question", "answer")
}


def chatbot_response(user_input):
    try:
        user_input = user_input.lower().strip()
        if not user_input:
            return "Xin vui lòng cho biết yêu cầu của bạn"

        # Khởi tạo history nếu chưa có
        if "history" not in user_context:
            user_context["history"] = []

        # Xử lý đặc biệt: Xóa ngữ cảnh
        if user_input == "xóa ngữ cảnh":
            xoa_ngucanh()
            user_context["history"] = []  # ✅ reset context
            user_context["previous_answers"] = luu_ngu_canh(
                "question", "answer")
            return "Ngữ cảnh đã được xóa."

        # Xử lý đặc biệt: Tiếp tục
        if user_input == "tiếp tục" and user_context.get("dk"):
            tiep = user_context.get("tiep")
            current_position = user_context.get("current_position", 0)
            if tiep:
                next_words = tieptuc_traloi(tiep, current_position)
                if next_words:
                    return next_words
                else:
                    return "Đã hết văn bản."
            else:
                return "Không có văn bản để trích xuất."

        # Trả lời theo đoạn văn ngữ cảnh
        text = xuli_doanvan_ngu_canh(user_input)
        if text:
            if len(text) >= 100000:
                user_response = traloi_theo_ngucanh1(user_input, text)
            else:
                user_response = traloi_theo_ngucanh2(user_input, text)
            chatgpt_output, updated_history = capnhat(
                user_input, user_response, user_context["history"])
            # ✅ giữ lại 10 cặp gần nhất
            user_context["history"] = updated_history[-20:]
            return chatgpt_output

        # Xử lý theo từ điển nội bộ
        ct1 = sau(user_input)
        ct2 = bay(user_input)

        if ct1 and ct2:
            output = tu_dien.get(ct1, "Xin lỗi, tôi chưa có câu trả lời.")
            luu_ngu_canh(user_input, output)
            return output

        if ct1 in danh_muc():
            if ct1 == "ngày mấy":
                return f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
            elif ct1 == "mấy giờ rồi":
                return f"Bây giờ là {datetime.now().strftime('%H:%M')}"
            return tu_dien.get(ct1, "Xin lỗi, tôi chưa có câu trả lời.")

        # Nếu không có câu trả lời -> tra Google
        user_response, tiep = search_google_1(user_input)
        user_context["tiep"] = tiep
        user_context["dk"] = True
        user_context["current_position"] = len(user_response.split())

        chatgpt_output, updated_history = capnhat(
            user_input, user_response, user_context["history"])
        user_context["history"] = updated_history[-20:]
        return chatgpt_output

    except Exception as e:
        return f"Lỗi: {str(e)}"


def danh_muc():
    return [
        "ngày mấy", "mấy giờ rồi", "đặt phòng", "thời tiết", "danh từ",
        "tính từ", "động từ", "xem ảnh", "thông dịch", "phiên dịch"
    ]


def main():
    previous_answers = luu_ngu_canh("question", "answer")

    def call_program_thongdichkokivy():
        subprocess.call(['python', 'thongdichkokivy.py'])

    random_responses = [
        "Xin lỗi, câu hỏi của bạn tôi chưa có thông tin, xin giúp tôi cập nhật cho tôi biết.",
        "xin lỗi, Tôi không thể trả lời câu hỏi của bạn, xin bạn hãy giúp tôi cập nhật.",
        "Xin lỗi, vấn đề bạn hỏi tôi chưa cập nhật, bạn có thể cung cấp thêm thông tin ?"
    ]
    list_cmd = [
        "Ok, Tôi sẵn sàng, xin bạn chờ trong giây lát",
        "Ok, mời bạn nghe thông tin thời tiết của chúng tôi",
        "Ok, mời bạn bắt đầu đăng ký đặt phòng.",
        "Ok, xin cho biết bạn trả phòng số mấy?",
        "OK Mời bạn xem hình em Ngọc Trinh",
        "Đã xem ảnh"
    ]

    chatgpt_output = ""
    conversation_history = []
    dk = False
    cv = True
    no_speech_count = 0
    tiep = ""

    history = []
    try:
        speak_text("Xin chào, tôi giúp được gì cho bạn?")
        data = pd.read_excel('sau.xlsx')
        data['Question'] = data['Question'].astype(str)
        data['Answer'] = data['Answer'].astype(str)

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
                user_question = user_input
                user_keywords = tach_tu_khoa(user_question)
                text = xuli_doanvan_ngu_canh(user_input)
                best_related_answer = None

                if text:
                    if len(text) >= 100000:
                        best_related_answer = traloi_theo_ngucanh1(
                            user_input, text)
                    else:
                        best_related_answer = traloi_theo_ngucanh2(
                            user_input, text)
                    print("thô: ", best_related_answer)
                if best_related_answer:
                    chatgpt_output, updated_history = capnhat(
                        user_input, best_related_answer, history)
                    history = updated_history[-20:]
                else:
                    ct1 = sau(user_input)
                    ct2 = bay(user_input)
                    if ct1 and ct2:
                        chatgpt_output, updated_history = capnhat(
                            user_input, tu_dien.get(ct1, random_responses[0]), history)
                        history = updated_history[-20:]
                        luu_ngu_canh(user_input, chatgpt_output)
                    elif ct1 in danh_muc() and not ct2:
                        if ct1 == "ngày mấy":
                            chatgpt_output = f"Hôm nay là {datetime.now().strftime('%d/%m/%Y')}"
                        elif ct1 == "mấy giờ rồi":
                            chatgpt_output = f"Bây giờ là {datetime.now().strftime('%H:%M')}"
                        else:
                            chatgpt_output = tu_dien.get(
                                ct1, random_responses[1])
                    else:
                        user_response, tiep = search_google_1(user_input)
                        dk = True
                        current_position = len(user_response.split())
                        chatgpt_output, updated_history = capnhat(
                            user_input, user_response, history)
                        history = updated_history[-20:]

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
