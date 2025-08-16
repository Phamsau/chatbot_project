from core.groq import lam_dep_cau_tra_loi_groq

# Giả định previous_answers được khởi tạo trong chatchinh.py và truyền vào nếu cần


def capnhat(user_input, user_response, history, sources=None):
    """Cập nhật đoạn hội thoại + xử lý câu trả lời sao cho đẹp, có trích nguồn"""
    if user_response:
        if sources:
            noi_dung_tham_khao = user_response + "\n\n🔗 Nguồn tham khảo:\n" + \
                "\n".join(f"- {src}" for src in sources)
        else:
            noi_dung_tham_khao = user_response

        chatgpt_output = lam_dep_cau_tra_loi_groq(
            user_input, noi_dung_tham_khao, history
        )

        history += [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": chatgpt_output}
        ]
    else:
        chatgpt_output = f"Xin lỗi, tôi không tìm thấy thông tin cho: {user_input}"

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
