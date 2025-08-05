# ngu_canh_truy_van.py
import re


# Danh sách đại từ mở rộng (ưu tiên cụm dài hơn trước)
DAI_TU_CHI_NGUOI = [
    "ông ấy", "bà ấy", "cô ấy", "cậu ấy", "anh ta", "chị ta", "anh ấy",
    "người ấy", "họ", "ông ta", "bà ta", "vị đó", "nhân vật đó", "ổng", "bả", "ảnh", "chỉ", "hắn", "hắn ta"
]

DAI_TU_CHI_DIA_DANH = [
    "nơi đó", "vùng đó", "khu vực đó", "thành phố đó", "quốc gia đó", "địa điểm đó", "tỉnh đó", "chổ đó", "ở đó", "tại đó", "chổ ấy", "nơi ấy"
]

DAI_TU_KHONG_PHAN = [
    "nó", "vật đó", "vật này", "chuyện đó", "việc ấy", "chủ đề đó", "việc đó",
    "con đó", "cái đó", "cái ấy", "chuyện ấy", "nó là", "hành động đó", "điều đó", "trường hợp đó"
]


def tao_truy_van_bo_sung(user_input: str, danh_tu_rieng_truoc_do: str = None, loai_thuc_the: str = "nguoi") -> str:
    if not danh_tu_rieng_truoc_do:
        return user_input.strip()

    if loai_thuc_the == "nguoi":
        tu_dai_dien = DAI_TU_CHI_NGUOI
    elif loai_thuc_the == "diadanh":
        tu_dai_dien = DAI_TU_CHI_DIA_DANH
    else:
        tu_dai_dien = []

    pattern = r'\b(' + '|'.join(map(re.escape, tu_dai_dien)) + r')\b'

    def thay_the(match):
        tu_goc = match.group(0)
        if tu_goc[0].isupper():
            return danh_tu_rieng_truoc_do.strip().capitalize()
        return danh_tu_rieng_truoc_do.strip()

    return re.sub(pattern, thay_the, user_input, flags=re.IGNORECASE).strip()
