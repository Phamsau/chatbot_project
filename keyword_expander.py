import re
# Stopwords để loại bỏ từ khóa nhiễu
STOPWORDS = {
    "gì", "nào", "ai", "sao", "à", "và", "các",
    "ấy", "thì", "đâu", "ra", "nó", "nhưng", "những", "hả", "sẽ", "mấy"
}
STOP_PHRASES = [
    "bao nhiêu", "như thế nào", "làm sao", "ở đâu", "khi nào", "là gì", "tại sao", "vì sao", "tại vì sao",
    "ai là", "ai đã", "ai đang", "có đúng không", "có phải là", "có thể", "có hay không", "có không",
    "nào là", "cái gì", "gì vậy", "thế nào", "cách nào", "phải không", "ra sao", "để làm gì",
    "mấy giờ", "mấy tuổi", "bao nhiêu", "kéo dài bao lâu",
    "bằng cách nào", "vì điều gì", "có nghĩa là gì", "được không", "được chứ", "bạn có biết", "là gì", "là ai", "có biết"
]
# Bộ mở rộng từ khóa theo loại câu hỏi
BO_TU_MO_RONG = {
    "trong": ["ngoài", "trên", "dưới", "trong"],
    "đó là gì": ["đó là", "gọi là", "được xem là", "đây là"],
    "ở đâu": ["ở", "tại", "nơi", "địa điểm", "quê", "xuất thân"],
    "khi nào": ["khi", "năm", "tháng", "ngày", "lúc", "thời gian", "thời điểm"],
    "vì sao": ["vì", "do", "tại vì", "bởi vì", "nguyên nhân", "lý do"],
    "như thế nào": ["như thế này", "cách", "ra sao", "mô tả", "kiểu", "dạng", "đặc điểm"],
    "bao nhiêu": ["số", "tổng", "khoảng", "chừng"],
    "đang làm gì": ["đang làm", "hành động", "thực hiện", "công việc"],
    "phu nhân": ["phu nhân", "vợ"],
    "chồng": ["chồng", "phu quân"],
    "triều đình": ["triều đình", "vua quan", "hoàng vương", "vua chúa", "hoàng triều"],
    "ông": ["ông", "cụ", "ngài", "lão"],
    "bà": ["bà", "cô", "mợ", "thím", "chị", "dì"],
    "đình": ["đình", "đền", "miếu", "chùa", "nơi thờ"],
    "quan": ["quan", "quan lại", "quan chức", "chức tước", "viên chức"],
    "quê": ["quê", "quán", "nơi sinh", "sinh sống", "hiện ở tại"],
    "chết": ["chết", "mất", "tử vong", "qua đời"],
    "hiện nay": ["đang", "hiện nay"]
}


def tach_tu_khoa(text):
    """Tách từ từ văn bản và loại bỏ stopwords."""
    words = text.split()
    keywords = [
        word.lower().rstrip(".,?!")
        for word in words
        if word.lower().rstrip(".,?!") not in STOPWORDS
    ]
    return keywords if keywords else [
        word.lower().rstrip(".,?!") for word in words
    ]


def tach_tu_khoa(text: str):
    """Tách các từ có nghĩa, loại bỏ stopwords đơn."""
    words = text.split()
    keywords = [
        word.lower().rstrip(".,?!")
        for word in words
        if word.lower().rstrip(".,?!") not in STOPWORDS
    ]
    return keywords if keywords else [w.lower().rstrip(".,?!") for w in words]


def loc_tu_quan_trong(cau_hoi: str):
    """Loại bỏ cụm từ dư thừa và chỉ giữ lại từ quan trọng."""
    cau_hoi = cau_hoi.lower()

    # Xử lý từng cụm stop-phrase chính xác theo từ nguyên
    for phrase in STOP_PHRASES:
        # Thêm khoảng trắng hai bên để không cắt dính vào từ
        pattern = r'\b' + re.escape(phrase) + r'\b'
        cau_hoi = re.sub(pattern, ' ', cau_hoi)

    # Xoá dấu câu sau khi xử lý stop phrases để không làm sai lệch khớp
    cau_hoi = re.sub(r"[^\w\s]", "", cau_hoi)

    # Loại stopwords đơn
    words = cau_hoi.split()
    return [w for w in words if w not in STOPWORDS]


def expand_keywords(user_input: str):
    """
    Trả về tập từ khóa mở rộng để tìm kiếm:
    - Tách từ chính trong input
    - Mở rộng theo nhóm nghĩa ưu tiên
    - Fix: không khớp sai từ do trùng chuỗi con (vd: 'ông' trong 'công')
    """
    base_keywords = tach_tu_khoa(user_input)
    question_lower = user_input.lower()
    mo_rong = []

    for nhom, cum_tu in BO_TU_MO_RONG.items():
        for phrase in cum_tu:
            # Khớp chính xác từ/cụm bằng regex để tránh khớp chuỗi con
            pattern = r'\b' + re.escape(phrase) + r'\b'
            if re.search(pattern, question_lower):
                mo_rong.extend(cum_tu)
                break

    # Tách cụm mở rộng thành từ đơn (giữ như code gốc)
    tu_don_tu_cum = []
    for cum in mo_rong:
        tu_don_tu_cum.extend(cum.lower().split())

    return list(set(base_keywords + tu_don_tu_cum))


def clean_text(text):
    # Tách token: từ, khoảng trắng, dấu câu
    tokens = re.findall(r'\w+|\s+|[^\w\s]', text, re.UNICODE)

    result = []
    for token in tokens:
        # Nếu là từ chữ (không phải dấu câu hay khoảng trắng)
        if re.fullmatch(r'\w+', token, re.UNICODE):
            if token.lower() in STOPWORDS:
                continue  # bỏ từ dừng nguyên vẹn
        result.append(token)

    return ''.join(result)
