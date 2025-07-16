from core.groq import lam_dep_cau_tra_loi_groq

# Giả định previous_answers được khởi tạo trong chatchinh.py và truyền vào nếu cần


def tach_tu_khoa(text):
    # Tách các từ từ văn bản
    words = text.split()
    # Loại bỏ các từ không cần thiết hoặc stop-words
    loai_bo = ["gì", "nào", "ai", "sao", "à", "và", "là", "các", "của",

               "ấy", "thì", "ở", "đâu", "vì", "ra", "nó", "nhưng", "những", "hả", "sẽ", "mấy"]
    cum_tu_khoa = [word.lower().rstrip(',.?!')
                   for word in words if word.lower().rstrip(',.?!') not in loai_bo]  # Loại bỏ dấu ',' và '.'
    if cum_tu_khoa == []:
        cum_tu_khoa = [word.lower()
                       for word in words if word.lower()]

        return cum_tu_khoa

    return cum_tu_khoa


# Hàm để xóa thông tin tra cứu khi kết thúc cuộc trò chuyện


def capnhat(user_input, user_response, history):
    if user_response:
        chatgpt_output = lam_dep_cau_tra_loi_groq(
            user_input, user_response, history)
        # lưu dữ liệu vào excel
        # ghi_dulieu(user_input, chatgpt_output)
        # Cập nhật history
        history += [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": chatgpt_output}
        ]
    else:
        chatgpt_output = "Xin lỗi, tôi không tìm thấy thông tin: " + user_input
    return chatgpt_output, history


def tieptuc_traloi(all_text, current_position):

    words = all_text.split()
    if current_position < len(words):
        next_words = words[current_position:current_position + 100]
        for word in words[current_position + 100:]:
            next_words.append(word)
            if word.endswith('.'):
                break  # Dừng khi gặp dấu chấm
        doan_tiep = ' '.join(next_words)
        current_position += len(doan_tiep.split())
        return doan_tiep
    else:
        return None  # Trả về None nếu đã hết văn bản
