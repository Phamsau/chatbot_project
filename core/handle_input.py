
import os
import random
import difflib

tu_dien = {}


def ghi_dulieu_txt(user_input, chatgpt_output, filename='sau.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{user_input.strip()}|{chatgpt_output.strip()}\n")
    global tu_dien
    tu_dien = doc_dulieu_txt(filename)


def doc_dulieu_txt(filename='sau.txt'):
    qa_dict = {}
    if not os.path.exists(filename):
        return qa_dict
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line:
                question, answer = line.strip().split('|', 1)
                qa_dict[question.strip()] = answer.strip()
    return qa_dict


tu_dien = doc_dulieu_txt()


def sau(user_input):
    matched_questions = []
    for question in tu_dien.keys():
        if isinstance(question, str):
            normalized_question = question.lower().strip()
            if normalized_question in user_input:
                matched_questions.append(question)
    if matched_questions:
        return random.choice(matched_questions)


def bay(user_input):
    matched_questions = []
    for question in tu_dien.keys():
        if isinstance(question, str):
            normalized_question = question.lower().strip()
            similarity = difflib.SequenceMatcher(
                None, normalized_question, user_input).ratio()
            if similarity > 0.9:
                matched_questions.append((question, similarity))
    if matched_questions:
        max_score = max(matched_questions, key=lambda x: x[1])[1]
        best_matches = [q for q, s in matched_questions if s == max_score]
        return random.choice(best_matches)
