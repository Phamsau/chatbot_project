from underthesea import pos_tag
from nghe_noi import recognize_speech, speak_text


def filter_nouns():
    # Phân tích cú pháp câu để đánh dấu loại từ (POS tagging)

    # Lọc danh từ chung
    nouns = [word for word, tag in tagged_words if tag in ['N']]
    return nouns


def filter_nouns1():

    # Lọc danh từ riêng
    nouns1 = [word for word, tag in tagged_words if tag in ['Np']]

    return nouns1


def filter_adjectives():

    # Lọc tính từ (A)
    adjectives = [word for word, tag in tagged_words if tag == 'A']

    return adjectives


def filter_verbs():

    # Lọc động từ (V)
    verbs = [word for word, tag in tagged_words if tag == 'V']

    return verbs


if __name__ == "__main__":

    speak_text("Mời bạn bắt đầu đọc một câu")
    input_sentence = input("User: ").strip().replace('\n', '')
    # Phân tích cú pháp câu để đánh dấu loại từ (POS tagging)
    tagged_words = pos_tag(input_sentence)
    print(tagged_words)
    nouns = filter_nouns()
    adjectives = filter_adjectives()
    verbs = filter_verbs()
    nouns1 = filter_nouns1()

    # Kiểm tra xem có kết quả không trước khi phát lại giọng nói.
    if nouns or adjectives or verbs or nouns1:
        speak_text("Mời bạn xem kết quả bên dưới")
        if nouns:
            speak_text("Danh từ chung: " + ", ".join(nouns))
            print("[PRINT]" + "Danh từ chung: ", nouns)
        if nouns1:
            speak_text("Danh từ riêng: " + ", ".join(nouns1))
            print("[PRINT]" + "Danh từ riêng: ", nouns1)
        if adjectives:
            speak_text("Tính từ: " + ", ".join(adjectives))
            print("[PRINT]" + "Tính từ: ", adjectives)
        if verbs:
            speak_text("Động từ: " + ", ".join(verbs))
            print("[PRINT]" + "Động từ: ", verbs)
