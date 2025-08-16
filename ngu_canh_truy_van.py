import re

# Hàm chuẩn hóa danh sách đại từ


def chuan_hoa_dai_tu(lst):
    return sorted({w.strip() for w in lst if w.strip()}, key=lambda x: -len(x))


# Danh sách đại từ
DAI_TU_CHI_NGUOI = chuan_hoa_dai_tu([
    "ông ấy", "bà ấy", "cô ấy", "cậu ấy", "chị ấy", "anh ta", "chị ta", "anh ấy", "cậu ấy", "con bé ấy", "ấy", "nó", "hắn",
    "người ấy", "họ", "ông ta", "bà ta", "vị đó", "nhân vật đó", "ổng", "bả", "ảnh", "chỉ", "hắn", "hắn ta"
])

DAI_TU_CHI_DIA_DANH = chuan_hoa_dai_tu([
    "nơi đó", "vùng đó", "khu vực đó", "thành phố đó", "quốc gia đó", "địa điểm đó", "tỉnh đó",
    "chỗ đó", "ở đó", "tại đó", "chỗ ấy", "nơi ấy"
])

DAI_TU_KHONG_PHAN = chuan_hoa_dai_tu([
    "nó", "vật đó", "vật này", "chuyện đó", "việc ấy", "chủ đề đó", "việc đó",
    "con đó", "cái đó", "cái ấy", "chuyện ấy", "nó là", "hành động đó", "điều đó", "trường hợp đó"
])

# Gom tất cả để thay thế khi cần
DAI_TU_DAI_DIEN = chuan_hoa_dai_tu(
    DAI_TU_CHI_NGUOI + DAI_TU_CHI_DIA_DANH + DAI_TU_KHONG_PHAN)

# Compile regex trước cho hiệu suất


def tao_regex(tu_dai_dien):
    pattern = r'(?<!\w)(' + '|'.join(map(re.escape, tu_dai_dien)) + r')(?!\w)'
    return re.compile(pattern, flags=re.IGNORECASE)


REGEX_NGUOI = tao_regex(DAI_TU_DAI_DIEN)
REGEX_DIADANH = tao_regex(DAI_TU_CHI_DIA_DANH)

# Loại bỏ cụm trùng lặp nhưng vẫn giữ nguyên dấu câu & layout


def loai_bo_trung_lap_cum(text: str) -> str:
    seen = set()
    result = []
    # Tách thành token bao gồm từ hoặc dấu câu
    tokens = re.findall(r'\w+|[^\w\s]', text, flags=re.UNICODE)
    for token in tokens:
        token_lower = token.lower()
        if token_lower not in seen:
            seen.add(token_lower)
            result.append(token)
    return " ".join(result).replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")

# Hàm chính


def tao_truy_van_bo_sung(user_input: str, danh_tu_rieng_truoc_do: str = None, loai_thuc_the: str = "nguoi") -> str:
    if not danh_tu_rieng_truoc_do:
        return user_input.strip()

    regex = REGEX_NGUOI if loai_thuc_the == "nguoi" else REGEX_DIADANH

    def thay_the(match):
        tu_goc = match.group(0)
        if tu_goc[0].isupper() or tu_goc.isupper():
            return danh_tu_rieng_truoc_do.strip().capitalize()
        return danh_tu_rieng_truoc_do.strip()

    if regex.search(user_input):
        cau_moi = regex.sub(thay_the, user_input).strip()
    else:
        cau_moi = f"{danh_tu_rieng_truoc_do.strip()} {user_input.strip()}"

    return loai_bo_trung_lap_cum(cau_moi)
