# ngu_canh_truy_van.py
import re


def tao_truy_van_bo_sung(user_input: str, danh_tu_rieng_truoc_do: str = None) -> str:
    """
    Thay thế tất cả đại từ mơ hồ xuất hiện trong user_input bằng danh_tu_rieng_truoc_do,
    ngay tại vị trí của chúng, giữ nguyên định dạng gốc của câu.
    """
    if not danh_tu_rieng_truoc_do:
        return user_input.strip()

    tu_dai_dien = [
        "ông ấy", "bà ấy", "họ", "nó", "cô ấy", "cậu ấy", "người ấy", "anh ta", "chị ta", "anh ấy",
        "hắn", "vị đó", "nhân vật đó", "vật đó", "vật này", "chuyện đó", "ông ta", "bà ta", "cái đó", "cái ấy", "chuyện ấy",
        "việc ấy", "chủ đề đó", "cái đó", "việc đó", "con đó", "nó là",
        "hành động đó", "điều đó", "trường hợp đó"
    ]

    # Ghép thành regex pattern, dùng \b để tránh khớp một phần từ
    pattern = r'\b(' + '|'.join(map(re.escape, tu_dai_dien)) + r')\b'

    # Hàm thay thế với giữ nguyên hoa thường của đại từ gốc
    def thay_the(match):
        tu_goc = match.group(0)
        # Nếu từ gốc viết hoa chữ cái đầu thì viết hoa danh_tu_rieng_truoc_do
        if tu_goc[0].isupper():
            return danh_tu_rieng_truoc_do.strip().capitalize()
        return danh_tu_rieng_truoc_do.strip()

    # Thay thế tất cả
    ket_qua = re.sub(pattern, thay_the, user_input, flags=re.IGNORECASE)

    return ket_qua.strip()
