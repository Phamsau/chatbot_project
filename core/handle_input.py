
import random
import pandas as pd
import difflib

data = pd.read_excel('sau.xlsx')
# Chuyển đổi các kiểu dữ liệu thành chuỗi văn bản
data['Question'] = data['Question'].astype(str)
data['Answer'] = data['Answer'].astype(str)
# Tạo từ điển qa_dict từ dữ liệu


def new_func(data):
    qa_dict = data.set_index('Question')['Answer'].to_dict()
    return qa_dict


tu_dien = new_func(data)


def sau(user_input):
    previous_answer = None
    matched_questions = []
    for question in tu_dien.keys():
        if isinstance(question, str) and not pd.isna(question):
            normalized_question = question.lower().strip()
            if normalized_question in user_input:
                matched_questions.append(question)
    if matched_questions:
        # Lọc danh sách các câu hỏi trùng lặp
        unique_matched_questions = list(set(matched_questions))
        # Nếu danh sách đã lọc vẫn chứa ít nhất một câu hỏi
        if unique_matched_questions:
            # Lọc ra các câu hỏi mà câu trả lời không trùng với câu trả lời trước đó
            eligible_questions = [
                q for q in unique_matched_questions if tu_dien[q] != previous_answer]
            # Nếu vẫn còn ít nhất một câu hỏi, chọn một câu hỏi ngẫu nhiên và cập nhật câu trả lời trước đó
            if eligible_questions:
                matched_question = random.choice(
                    eligible_questions)
                return matched_question


def bay(user_input):
    matched_questions = []
    for question in tu_dien.keys():
        if isinstance(question, str) and not pd.isna(question):
            normalized_question = question.lower().strip()
            similarity_score = difflib.SequenceMatcher(
                None, normalized_question, user_input).ratio()
            # Chỉ thêm câu hỏi vào danh sách nếu độ tương đồng lớn hơn một ngưỡng nhất định (ví dụ: 0.6)
            if similarity_score > 0.9:
                matched_questions.append(
                    (question, similarity_score))
    if matched_questions:
        # Lọc ra các câu hỏi có độ tương đồng cao nhất
        max_similarity = max(
            matched_questions, key=lambda x: x[1])[1]
        best_matched_questions = [
            (q, score) for q, score in matched_questions if score == max_similarity]
        # Chọn ngẫu nhiên một trong số các câu hỏi có độ tương đồng cao nhất
        matched_question = random.choice(
            best_matched_questions)[0]
        return matched_question
