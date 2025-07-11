
import pandas as pd


def ghi_dulieu(user_input, chatgpt_output):
    new_data = pd.DataFrame(
        {"Question": [user_input], "Answer": [chatgpt_output]})
    existing_data = pd.read_excel('sau.xlsx') if pd.read_excel(
        'sau.xlsx') is not None else pd.DataFrame()
    updated_data = pd.concat(
        [existing_data, new_data], ignore_index=True)
    updated_data.to_excel('sau.xlsx', index=False)


def doc_dulieu():
    # Đọc dữ liệu từ file Excel
    data = pd.read_excel('sau.xlsx')
    # Chuyển đổi các kiểu dữ liệu thành chuỗi văn bản
    data['Question'] = data['Question'].astype(str)
    data['Answer'] = data['Answer'].astype(str)
    qa_dict = data.set_index('Question')['Answer'].to_dict()
    # Tạo từ điển qa_dict từ dữ liệu
    # tu_dien = new_func(data)
    return qa_dict
