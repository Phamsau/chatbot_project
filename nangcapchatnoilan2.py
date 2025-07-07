import openai
from nghe_noi import recognize_speech, speak_text, recognize_speech1, speak_text1
import os
from openpyxl import Workbook
import speech_recognition as sr
import pandas as pd
import random
from pydub.playback import play
import difflib

# Thiết lập mô hình ngôn ngữ và nhiệt độ mặc định
model_engine = "gpt-3.5-turbo"
temperature = 0.7
max_tokens = 200

# Khởi tạo workbook và worksheet
workbook = Workbook()
worksheet = workbook.active
worksheet["A1"] = "User"
worksheet["B1"] = "ChatBOT"

# Khởi tạo biến lưu trữ các câu hỏi và câutrả lời trước đó
conversation_history = []

# Kiểm tra xem có tệp tin API key đã tồn tại hay chưa
api_key_file = "openai_api_key.txt"
if os.path.isfile(api_key_file):
    with open(api_key_file, "r") as f:
        openai_api_key = f.readline().strip()
else:
    openai_api_key = input("Nhập API key: ")
    with open(api_key_file, "w") as f:
        f.write(openai_api_key)

# Thiết lập thông tin xác thực API của OpenAI
openai.api_key = openai_api_key
prompt = ""


def get_chatgpt_response(user_input):
    # Biến toàn cục để lưu lịch sử hội thoại dưới dạng messages
    global conversation_history

    # Nếu chưa có lịch sử hội thoại thì khởi tạo
    if not conversation_history:
        conversation_history = [
            {"role": "system", "content": "Bạn là một trợ lý AI thân thiện."}]

    # Thêm câu hỏi của người dùng vào lịch sử
    conversation_history.append({"role": "user", "content": user_input})

    # Gửi yêu cầu tới OpenAI Chat API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Hoặc "gpt-4" nếu bạn có quyền truy cập
        messages=conversation_history,
        temperature=0.7,
        max_tokens=200,
    )

    # Lấy phản hồi từ chatbot
    chatgpt_output = response['choices'][0]['message']['content'].strip()

    # Thêm phản hồi vào lịch sử để duy trì cuộc trò chuyện
    conversation_history.append(
        {"role": "assistant", "content": chatgpt_output})

    return chatgpt_output


matched_questions = []


def new_func(data):
    qa_dict = data.set_index('Question')['Answer'].to_dict()
    return qa_dict


def sau(user_input):
    matched_questions = []
    previous_answer = None
    for question in qa_dict.keys():
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
                q for q in unique_matched_questions if qa_dict[q] != previous_answer]

            # Nếu vẫn còn ít nhất một câu hỏi, chọn một câu hỏi ngẫu nhiên và cập nhật câu trả lời trước đó
            if eligible_questions:
                matched_question = random.choice(
                    eligible_questions)
                return matched_question


def bay(user_input):

    matched_questions = []
    for question in qa_dict.keys():
        if isinstance(question, str) and not pd.isna(question):
            normalized_question = question.lower().strip()
            similarity_score = difflib.SequenceMatcher(
                None, normalized_question, user_input).ratio()
            # Chỉ thêm câu hỏi vào danh sách nếu độ tương đồng lớn hơn một ngưỡng nhất định (ví dụ: 0.6)
            if similarity_score > 0.8:
                matched_questions.append(
                    (question, similarity_score))
    if matched_questions:
        # Lọc ra các câu hỏi có độ tương đồng cao nhất
        max_similarity = max(matched_questions, key=lambda x: x[1])[1]
        best_matched_questions = [
            (q, score) for q, score in matched_questions if score == max_similarity]
        # Chọn ngẫu nhiên một trong số các câu hỏi có độ tương đồng cao nhất
        matched_question = random.choice(best_matched_questions)[0]
        return matched_question


# tạo hàm trả lời ngẫu nhiên
random_responses = [
    "Xin lỗi, câu hỏi của bạn tôi chưa có thông tin, xin giúp tôi cập nhật cho tôi biết.",
    "xin lỗi, Tôi không thể trả lời câu hỏi của bạn, xin bạn hãy giúp tôi cập nhật.",
    "Xin lỗi, vấn đề bạn hỏi tôi chưa cập nhật, bạn có thể cung cấp thêm thông tin ?"
]
conversation_history = []
no_speech_count = 0
while True:

    user_input = recognize_speech1().strip().replace('\n', '')

    if user_input.lower() == "":
        no_speech_count = no_speech_count + 1
    else:
        no_speech_count = 0

    if user_input.strip().lower() in ["stop", "ok ok"]:
        speak_text1(" chát bót xin tạm biệt và hẹn gặp lại")
        break
    else:

        # Đọc dữ liệu từ file Excel
        data = pd.read_excel('sau.xlsx')

        # Chuyển đổi dữ liệu thành từ điển
        qa_dict = data.set_index('Question')['Answer'].to_dict()

        # Xử lý câu hỏi từ người dùng
        matched_question = None
        user_input = user_input.lower().strip()  # Chuẩn hóa câu hỏi người dùng

        if user_input == "ok ok" or no_speech_count >= 2:
            chatgpt_output = " xin chào tạm biệt, hẹn gặp lại  "
            text = ""
            break
        else:
            ct1 = sau(user_input)
            ct2 = bay(user_input)

            # if ct1 and not ct2:
            #   tt = ct1
            # elif ct2 and not ct1:
            #   tt = ct2
            # else:
            ct3 = [ct1, ct2]
            tt = random.choice(ct3)
            if tt:
                chatgpt_output = qa_dict[tt]

            elif user_input == "":
                chatgpt_output = "Xin bạn hãy nói gì đó"

            else:
                text = user_input
                chatgpt_output = get_chatgpt_response(text)

                # NN_output = random.choice(random_responses)
                # speak_text(NN_output + user_input)

                # Yêu cầu người dùng cung cấp thông tin
                # user_response = recognize_speech().strip().replace('\n', '')

                # if user_response:
                # chatgpt_output = user_response
                # speak_text("Thông tin của bạn đã được cập nhật")

                # Lưu câu hỏi và câu trả lời mới vào DataFrame
                new_data = pd.DataFrame(
                    {"Question": [user_input], "Answer": [chatgpt_output]})

                # Đọc dữ liệu từ tệp Excel hiện có (nếu có)
                existing_data = pd.read_excel('sau.xlsx') if pd.read_excel(
                    'sau.xlsx') is not None else pd.DataFrame()

                # Kết hợp dữ liệu mới và dữ liệu hiện có
                updated_data = pd.concat(
                    [existing_data, new_data], ignore_index=True)

                # Lưu lại dữ liệu vào tệp Excel
                updated_data.to_excel('sau.xlsx', index=False)

                # else:
                # chatgpt_output = "Cảm ơn bạn, hi vọng lần sau bạn sẽ cung cấp thông tin cho tôi"

    conversation_history.append(user_input)
    conversation_history.append(chatgpt_output)
    # In câu trả lời và yêu cầu của người dùng ra màn hình
    print("Chatbot: ", chatgpt_output)
    speak_text1(chatgpt_output)
    # Lưu câu trả lời và yêu cầu của người dùng vào worksheet
