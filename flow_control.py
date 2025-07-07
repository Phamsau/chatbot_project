import subprocess
from datphong import tra_phong


# Các chương trình được gọi bằng subprocess


def call_program_tinthoitiet():
    subprocess.call(['python', 'tinthoitiet.py'])


def call_program_chatgpt():
    subprocess.call(['python', 'nangcapchatnoilan2.py'])


def call_program_hinhanh(image_name=""):
    subprocess.call(['python', 'D:\\letan\\hinhanh.py', image_name])


def call_program_lodanhtu():
    subprocess.call(['python', 'lodanhtu.py'])


def call_program_datphong():
    subprocess.call(['python', 'datphong.py'])


def call_program_thongdichkokivy():
    subprocess.call(['python', 'thongdichkokivy.py'])


def call_tra_phong():
    tra_phong()


def execute_command(chatgpt_output):

    if chatgpt_output == "Ok, Tôi sẵn sàng, xin bạn chờ trong giây lát":
        call_program_lodanhtu()
        pass
    if chatgpt_output == "Ok, mời bạn nghe thông tin thời tiết của chúng tôi":
        call_program_tinthoitiet()
        pass
    if chatgpt_output == "Ok, mời bạn bắt đầu đăng ký đặt phòng.":
        call_program_datphong()
        pass
    if chatgpt_output == "Ok, mời bạn bắt đầu trò chuyện với chatbot":
        call_program_chatgpt()
        pass
    if chatgpt_output == "Ok, xin cho biết bạn trả phòng số mấy?":
        call_tra_phong()
        pass
    if chatgpt_output == "ok, tôi sẵn sàng thông dịch cho bạn":
        call_program_thongdichkokivy()
        chatgpt_output = "cảm ơn bạn"
    if chatgpt_output == "OK Mời bạn xem hình em Ngọc Trinh":
        if not image_viewed:
            call_program_hinhanh()
            image_viewed = True
            chatgpt_output = "Đã xem ảnh"
        else:
            chatgpt_output = "Bạn đã xem ảnh rồi"
    if chatgpt_output == "Đã xem ảnh":
        waiting_for_face = True
        image_viewed = False
