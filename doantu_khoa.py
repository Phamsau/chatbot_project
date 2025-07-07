
from nltk.util import ngrams
from collections import defaultdict
import random
from underthesea import word_tokenize


def loai_bo(words):
    # Loại bỏ các từ không cần thiết hoặc stop-words
    loai_bo = ["gì", "nào", "ai", "sao",
               "ấy", "thì", "ở", "đâu", "vì", "ra", "của", "nó", "nhưng", "hả", "sẽ", "mấy", "là", ",", "'", ".", "và"]
    words = word_tokenize(words)
    cum_tu_khoa = [word.lower()
                   for word in words if word.lower() not in loai_bo]  # Loại bỏ dấu ',' và '.'
    if cum_tu_khoa:
        return cum_tu_khoa
    else:
        return words


def text_ngrams(keyword, text, num_words=4):
    keyword = word_tokenize(keyword)
    if keyword:
        current_word = random.choice(keyword)
        print("tt: ", current_word)
    else:
        return
    generated_text = []
    for line in text:
        line = line.strip()  # Xóa các ký tự trắng thừa
        if line:  # Kiểm tra xem dòng có nội dung hay không
            tokens = loai_bo(line)

        print(tokens)
        lower_tokens = [token.lower() for token in tokens]
        # Tổng số bigrams trong văn bản
        total_bigrams = len(lower_tokens) - 1

        word_dict = defaultdict(list)
        word_frequency = defaultdict(int)

        # Tính toán tần suất xuất hiện của các bigrams và các từ
        for first, second in ngrams(lower_tokens, 2):
            word_dict[first].append(second)
            word_frequency[(first, second)] += 1

        for _ in range(num_words):
            # Kiểm tra xem current_word có phải là danh sách không
            if isinstance(current_word, list):
                break

            next_words = word_dict.get(current_word, [])
            if not next_words:
                break

                # Tính toán xác suất dựa trên tần suất xuất hiện của bigrams
                probabilities = [
                    word_frequency[(current_word, word)] / total_bigrams for word in next_words]

                # Chọn ngẫu nhiên từ dựa trên xác suất
                next_word = random.choices(
                    next_words, weights=probabilities)[0]

                generated_text.append(next_word)
                current_word = next_word
                print(current_word)
        generated_text_with_case = keyword + generated_text
        generated_text = ' '.join(generated_text_with_case)
        return generated_text.capitalize() + '...'
