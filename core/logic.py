

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


def tukhoa_tra_ngu_canh(user_keywords, previous_answers):
    max_similarity_percentage = 0
    # Danh sách để lưu trữ tất cả các đoạn văn bản có tỷ lệ tương đồng cao nhất
    max_similar_answers = []

    for previous_question, previous_answer in previous_answers.items():
        previous_answer_paragraphs = previous_answer.split('\n')
        for paragraph in previous_answer_paragraphs:
            previous_keywords = tach_tu_khoa(paragraph)
            common_keywords = set(user_keywords) & set(previous_keywords)
            similarity_percentage = len(common_keywords) / len(user_keywords)
            if similarity_percentage >= max_similarity_percentage:
                if similarity_percentage > max_similarity_percentage:
                    # Nếu có tỷ lệ tương đồng mới lớn hơn, cập nhật danh sách và tỷ lệ tương đồng
                    max_similarity_percentage = similarity_percentage
                    max_similar_answers = [paragraph]

                else:
                    # Nếu tỷ lệ tương đồng bằng, thêm vào danh sách
                    max_similar_answers.append(paragraph)

    if max_similarity_percentage >= 0.55:
        # print("kết quả: " ' '.join(max_similar_answers))
        return ' '.join(max_similar_answers)
    else:
        return None


# Hàm để xóa thông tin tra cứu khi kết thúc cuộc trò chuyện


def capnhat(user_response):
    if user_response:
        chatgpt_output = user_response

        # new_data = pd.DataFrame(
        # {"Question": [user_input], "Answer": [chatgpt_output]})
        # existing_data = pd.read_excel('sau.xlsx') if pd.read_excel(
        # 'sau.xlsx') is not None else pd.DataFrame()
        # updated_data = pd.concat(
        # [existing_data, new_data], ignore_index=True)
        # updated_data.to_excel('sau.xlsx', index=False)
    else:
        # print(kq)
        chatgpt_output = (
            "xin lỗi tôi không tìm thấy thông tin ")
    return chatgpt_output


def tieptuc_traloi(all_text, current_position):

    words = all_text.split()
    if current_position < len(words):
        next_words = words[current_position:current_position + 100]
        current_position += 99
        return ' '.join(next_words)
    else:
        return None  # Trả về None nếu đã hết văn bản
