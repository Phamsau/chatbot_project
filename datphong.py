import openpyxl
import os
import pandas as pd
import random
from openpyxl.styles import Alignment
from datetime import datetime
from nghe_noi import recognize_speech, speak_text


def dat_phong():
    # Yêu cầu người dùng cung cấp thông tin đặt phòng
    speak_text("Xin cho biết họ tên người đặt phòng.")
    ho_ten = recognize_speech().strip().replace('\n', '')
    speak_text("Xin vui lòng cho biết loại phòng (phòng đơn hay phòng đôi).")
    loai_phong = recognize_speech().strip().replace('\n', '')

    if loai_phong in ["phòng đơn", "hằng đơn", "phòng đơn", "vòng đơn", "phản đơn"]:
        loai_phong = "phòng đơn"

    if loai_phong in ["phòng đôi", "phòng đâu", "phần đôi", "Phận Đời", "phận đôi", "phản đâu", "cặp đôi", "vòng đâu", "hàng đầu", "hàng đâu", "vòng đôi", "phản đối", "phản đôi", "phận đời"]:
        loai_phong = "phòng đôi"

    if loai_phong not in ["phòng đơn", "phòng đôi"]:
        speak_text("Loại phòng không hợp lệ. Vui lòng đăng ký lại.")
        return

    # Kiểm tra loại phòng và chỉ định phòng trống
    if loai_phong == "phòng đơn":
        # Sử dụng loại phòng 'phòng đơn'
        phong_trong = tim_phong_trong('datphong.xlsx', 'Sheet1', 'phòng đơn')
    elif loai_phong == "phòng đôi":
        # Sử dụng loại phòng 'phòng đôi'
        phong_trong = tim_phong_trong('datphong.xlsx', 'Sheet1', 'phòng đôi')

    if not phong_trong:
        speak_text("Xin lỗi, không còn phòng trống loại {}.".format(loai_phong))
        return

    # Chọn ngẫu nhiên một phòng trống
    so_phong = random.choice(phong_trong)

    # Lấy ngày hiện tại
    ngay_nhan_phong = datetime.now().strftime("%d/%m/%Y")

    # Cập nhật thông tin đặt phòng vào DataFrame
    new_data = pd.DataFrame({
        "Họ tên người đặt phòng": [ho_ten],
        "Loại phòng": [loai_phong],
        "Phòng số": [so_phong],
        "Ngày nhận phòng": [ngay_nhan_phong],
        "Ngày trả phòng": [""],
        "Thời gian lưu trú": [""]
    })

    # Ghi thông tin đặt phòng vào tệp "datphong.xlsx"
    existing_data = pd.read_excel('datphong.xlsx') if os.path.isfile(
        'datphong.xlsx') else pd.DataFrame()
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    updated_data.to_excel('datphong.xlsx', index=False)

    # Định dạng lại tệp Excel
    column_widths = {
        'A': 30,
        'B': 15,
        'C': 20,
        'D': 15,
        'E': 15,
        'F': 15
    }
    format_excel('datphong.xlsx', 'Sheet1', column_widths)

    speak_text(
        "Đặt phòng thành công. Phòng {} đã được đặt cho bạn. Chúc bạn có kỳ nghỉ vui vẻ".format(so_phong))


def tra_phong():

    # Đọc dữ liệu từ tệp Excel
    data = pd.read_excel('datphong.xlsx')
    # Mở tệp Excel

    # Chuyển đổi các kiểu dữ liệu thành chuỗi văn bản
    data['Phòng số'] = data['Phòng số'].astype(str)

    sophong = recognize_speech().strip().replace('\n', '')

    if any(data['Phòng số'] == sophong):

        # Lấy ngày trả phòng hiện tại
        ngay_tra_phong = datetime.now().strftime("%d/%m/%Y")

        # Lấy ngày nhận phòng từ DataFrame
        ngay_nhan_phong = data.loc[data['Phòng số']
                                   == sophong, 'Ngày nhận phòng'].iloc[-1]

        # xác định dòng chứa thông tin phòng cần trả
        row_index = data[data['Phòng số'] == sophong].index[-1]
        # Cập nhật thông tin trả phòng và tính thời gian lưu trú
        if pd.notnull(data.at[row_index, 'Ngày trả phòng']):
            speak_text(
                "Không tìm thấy thông tin về phòng {}. Vui lòng kiểm tra lại.".format(sophong))
            return
        else:
            data.at[row_index, 'Ngày trả phòng'] = ngay_tra_phong

            ngay_nhan_phong = datetime.strptime(ngay_nhan_phong, "%d/%m/%Y")
            ngay_tra_phong = datetime.strptime(ngay_tra_phong, "%d/%m/%Y")
            thoi_gian_lu_tru = ngay_tra_phong - ngay_nhan_phong

            data.at[row_index, 'Thời gian lưu trú'] = thoi_gian_lu_tru.days

            # Ghi thông tin vào tệp "datphong.xlsx" mà không thay đổi định dạng kích thước cột
            data.to_excel('datphong.xlsx', index=False, engine='openpyxl')
            pass
        print("Thông tin lưu trú của bạn: "
              "Ngày nhận phòng: ", ngay_nhan_phong,
              "Ngày trả phòng: ",  ngay_tra_phong,
              "Thời gian lưu trú: ", thoi_gian_lu_tru)
        speak_text(
            "Phòng {} đã được trả. Cảm ơn quý khách đã sử dụng dịch vụ của chúng tôi.".format(sophong))
        # Định dạng lại tệp Excel
        column_widths = {
            'A': 30,
            'B': 15,
            'C': 20,
            'D': 15,
            'E': 15,
            'F': 15
        }
        format_excel('datphong.xlsx', 'Sheet1', column_widths)
    else:
        speak_text(
            "Không tìm thấy thông tin về phòng {}. Vui lòng kiểm tra lại.".format(sophong))


def tim_phong_trong(file_path, sheet_name, column):
    # Đọc dữ liệu từ tệp Excel
    data = pd.read_excel(file_path, sheet_name=sheet_name)

    # Lấy danh sách số phòng đã có trong cột "ngày nhận phòng" nhưng chưa có trong cột "ngày trả phòng"
    phong_da_dat = data[data['Ngày trả phòng'].isnull()]['Phòng số'].tolist()
    print("[PRINT]" + "phòng đã đặt chưa trả:  ", phong_da_dat)

    if column == 'phòng đơn':
        phong_tat_ca = ['101', '103', '105', '107', '109',
                        '111', '113']  # Danh sách phòng đơn của khách sạn
    elif column == 'phòng đôi':
        phong_tat_ca = ['201', '203', '205', '207', '209',
                        '211', '213']  # Danh sách phòng đôi của khách sạn
    print("[PRINT]" + column, phong_tat_ca)
    # Tìm danh sách phòng trống bằng cách loại bỏ các số phòng đã được đặt từ danh sách phòng đầy đủ
    phong_trong = [phong for phong in phong_tat_ca if str(
        phong) not in [str(p) for p in phong_da_dat]]
    print("[PRINT]" + "Phòng Trống: ", column, phong_trong)
    return phong_trong


def format_excel(file_path, sheet_name, column_widths):
    # Định dạng ô trong tệp Excel
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook[sheet_name]

    # Định dạng chiều rộng cột
    for column, width in column_widths.items():
        sheet.column_dimensions[column].width = width

    # Định dạng căn lề ô
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')

    workbook.save(file_path)
    workbook.close()


if __name__ == "__main__":
    dat_phong()
