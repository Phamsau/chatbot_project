from collections import defaultdict
from nltk.util import ngrams
from underthesea import word_tokenize
import random
from collections import Counter
import re
import sys
import time


def xuli_nn(text):
    global used_words
    used_words = set()
    tokens = word_tokenize(text)
    upper_tokens = [token for token in tokens if token[0].isupper()]
    lower_tokens = [token.lower() for token in tokens]
    word_counts = Counter(lower_tokens)
    reusable_words = [word for word, count in word_counts.items() if count > 1]
    bigrams = list(ngrams(lower_tokens, 2))

    word_dict = defaultdict(list)

    for first, second in bigrams:
        word_dict[first].append(second)

    if len(lower_tokens) <= 3:
        return text
    else:
        current_word = lower_tokens[3]
        word3 = lower_tokens[:3]
        generated_text = [current_word]
        word_count = len(lower_tokens)
        for _ in range(word_count):
            # Lấy danh sách từ tiếp theo hoặc rỗng nếu không có
            next_words = word_dict.get(current_word, [])
            # used_words = set(word for word in used_words)
            tusd = set(
                word for word in used_words if word not in reusable_words)  # used_words = set(word for word in used_words)
            available_words = [
                word for word in next_words if word not in tusd]

            if not available_words:
                break
            next_word = random.choice(available_words)
            generated_text.append(next_word)
            current_word = next_word
            used_words.add(current_word)
        generated_text_with_case = [word3[0]] + \
            word3[1:] + [word for word in generated_text]
        generated_text = ' '.join(generated_text_with_case)
        for word in upper_tokens:
            generated_text = generated_text.replace(word.lower(), word)
        return remove_redundant_phrases(generated_text)


def xuli_nn1(text):
    global used_words
    used_words = set()

    tokens = word_tokenize(text)
    upper_tokens = [token for token in tokens if token[0].isupper()]
    lower_tokens = [token.lower() for token in tokens]
    word_counts = Counter(lower_tokens)
    reusable_words = [word for word, count in word_counts.items() if count > 1]
    bigrams = list(ngrams(lower_tokens, 2))

    word_dict = defaultdict(list)
    for first, second in bigrams:
        word_dict[first].append(second)

    if len(lower_tokens) <= 3:
        return text
    else:
        current_word = lower_tokens[3]
        generated_text = lower_tokens[:3]  # Giữ nguyên 3 từ đầu tiên
        word_count = len(lower_tokens)

        for _ in range(word_count - 3):  # Trừ 3 từ đầu tiên
            next_words = word_dict.get(current_word, [])
            available_words = [
                word for word in next_words if word not in used_words]

            # Sử dụng từ có tần suất cao hơn
            if available_words:
                next_word = max(available_words, key=lambda w: word_counts[w])
            else:
                break  # Kết thúc nếu không còn từ khả dụng

            generated_text.append(next_word)
            current_word = next_word
            used_words.add(current_word)

        generated_text_with_case = ' '.join(generated_text)

        # Khôi phục từ in hoa trong văn bản gốc
        for word in upper_tokens:
            generated_text_with_case = generated_text_with_case.replace(
                word.lower(), word)

        return generated_text_with_case


def remove_redundant_phrases(text):
    # Tách văn bản thành các câu dựa trên dấu chấm
    sentences = re.split(r'[.]', text)
    processed_sentences = []

    seen_sentences = set()
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence not in seen_sentences:
            seen_sentences.add(sentence)
            # Tách câu thành các cụm từ dựa trên dấu phẩy và loại bỏ khoảng trắng thừa
            phrases = [phrase.strip()
                       for phrase in re.split(r'[ ]', sentence) if phrase]

            # Loại bỏ cụm từ lặp lại
            unique_phrases = []
            for phrase in phrases:
                if phrase not in unique_phrases:
                    unique_phrases.append(phrase)

            # Ghép lại các cụm từ thành câu
            if unique_phrases:
                processed_sentence = ' '.join(unique_phrases)
                processed_sentences.append(processed_sentence)

    # Ghép lại các câu thành đoạn văn
    return '. '.join(processed_sentences) + '.'


def tao_duong_vien(text):
    lines = text.split('\n')  # Tách văn bản thành từng dòng
    # Xác định chiều dài lớn nhất của dòng văn bản
    k = len(text.lower())
    if k < 60-1:
        max_length = k
    else:
        max_length = 60
    # Tạo đường viền dựa trên chiều dài lớn nhất
    border = '.' + '-' * (max_length + 2) + '.'

    result = border + '\n'  # Bắt đầu với đường viền ở đầu văn bản
    for line in lines:
        words = line.split()
        new_line = ''
        for word in words:
            if len(new_line + word) <= max_length - 1:
                new_line += word + ' '
            else:
                result += f'| {new_line.ljust(max_length)} |\n'
                new_line = word + ' '
        if new_line:
            result += f'| {new_line.ljust(max_length)} |\n'

    result += border  # Kết thúc với đường viền ở cuối văn bản

    return result


def con_tro(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.005)


def con_tro_1(text, delay=0.005):
    result = ""
    for char in text:
        result += char
        time.sleep(delay)
    return result


def hien_thi_vien_va_con_tro(text):
    vien_text = tao_duong_vien(text)
    for line in vien_text.split('\n'):
        if line.startswith('|'):
            con_tro(line + '\n')
        else:
            print(line)
