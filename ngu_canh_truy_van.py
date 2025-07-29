# ngu_canh_truy_van.py

def co_can_bo_sung_chu_de(user_input: str) -> bool:
    """
    Kiểm tra xem user_input có chứa đại từ hoặc từ chỉ mơ hồ,
    nếu có thì cần bổ sung chủ đề (danh từ riêng) vào câu hỏi.
    """
    tu_dai_dien = [
        "ông ấy", "bà ấy", "họ", "nó", "cô ấy", "cậu ấy", "người ấy", "anh ta", "chị ta", "ông", "bà",
        "vị đó", "nhân vật đó", "vật đó", "vật này", "chuyện đó", "việc ấy", "chủ đề đó",
        "nó là gì", "việc đó", "hành động đó", "điều đó", "trường hợp đó"
    ]
    user_input = user_input.lower()
    return any(cum in user_input for cum in tu_dai_dien)


def tao_truy_van_bo_sung(user_input: str, danh_tu_rieng_truoc_do: str = None) -> str:
    """
    Nếu câu hỏi cần thêm chủ đề thì nối chủ đề cũ vào đầu câu hỏi.
    Nếu không, trả lại nguyên văn user_input.
    """
    if danh_tu_rieng_truoc_do and co_can_bo_sung_chu_de(user_input):
        return f"{danh_tu_rieng_truoc_do.strip()} {user_input.strip()}"
    return user_input.strip()
