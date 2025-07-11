
from googlesearch import search  # Cần cài đặt: pip install googlesearch-python
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from difflib import SequenceMatcher
import random
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
import time
from underthesea import word_tokenize
previous_answers = {}


def luu_ngu_canh(question, answer, MAX_QUESTIONS=1):
    if len(previous_answers) >= MAX_QUESTIONS:
        oldest_question = next(iter(previous_answers))  # Lấy câu hỏi cũ nhất
        del previous_answers[oldest_question]  # Xóa câu hỏi cũ nhất
    # Lưu câu hỏi và câu trả lời mới vào từ điển
    previous_answers[question] = answer
    return previous_answers


def xoa_ngucanh():
    return previous_answers.clear()


def xuly_vanban_google(keyword, all_text):
    # Chuyển cả từ khóa và văn bản về chữ thường
    keyword = keyword.lower()
    all_text_lower = all_text.lower()
    # Tìm vị trí xuất hiện đầu tiên của từ trong all_text nằm trong từ khóa
    start_index = len(all_text)
    for word in keyword.split():
        if word in all_text_lower.split():
            word_index = all_text_lower.index(word)
            if word_index < start_index:
                start_index = word_index

    # Bắt đầu lấy đoạn văn bản từ vị trí xuất hiện của từ trong từ khóa
    if start_index != len(all_text):
        all_text = all_text[start_index:]
    return all_text  # Trả về phần văn bản được lấy ra từ vị trí đầu tiên của từ khóa


def search_google_1(keyword, num_of_results=10, max_sources=2, max_words=100):

    try:
        search_results = search(keyword, num_results=num_of_results, lang='vi')
        all_paragraphs = []
        sources_count = 0

        for first_link in search_results:
            if sources_count >= max_sources:
                break

            if not first_link:
                continue

            try:
                response = requests.get(first_link, timeout=10, verify=False)
                time.sleep(random.uniform(1, 3))  # Sleep để tránh bị chặn

                soup = BeautifulSoup(response.content, 'html.parser')

                # Xoá các thẻ không mong muốn
                for tag in soup(['script', 'style', 'footer', 'header', 'nav', 'aside', 'address']):
                    tag.decompose()

                # Lấy các đoạn văn <p>, thêm separator để không dính chữ
                paragraphs = [
                    p.get_text(separator=" ", strip=True)
                    for p in soup.find_all('p')
                    if p.get_text(strip=True)
                ]

                all_paragraphs.extend(paragraphs)
                sources_count += 1

            except requests.RequestException as e:
                # print(f"Không thể truy cập trang {first_link}: {e}")
                pass

        if not all_paragraphs:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp"

        # Kết hợp và làm sạch văn bản
        all_text = '\n'.join(filter(None, all_paragraphs))
        # Xoá khoảng trắng thừa trước dấu câu
        all_text = re.sub(r'\s+([.,;!?])', r'\1', all_text)

        # Các bước làm sạch đặc biệt (theo yêu cầu trước)
        patterns_to_remove = [
            r'Hãy xác nhận rằng quý vị là chuyên gia chăm sóc sức khỏe',
            r'Liên kết bạn vừa chọn sẽ đưa bạn tới trang web của một bên thứ ba.*?nội dung khác về y tế có liên quan\.',
            r'\(.*?\)', r'\[.*?\]', r'\|.*?\|', r'[_*|()]'
        ]
        for pattern in patterns_to_remove:
            all_text = re.sub(pattern, '', all_text, flags=re.DOTALL)

        # Thêm hàm xử lý văn bản nếu có
        try:
            all_text = xuly_vanban_google(keyword, all_text)
        except:
            pass  # Nếu không có hàm này thì bỏ qua

        # Backup version xoá \n thành space
        text = all_text.replace("\n", " ")

        if text.strip():
            try:
                luu_ngu_canh(keyword, text)
            except:
                pass
        # Giới hạn số từ
        words = all_text.split()
        if len(words) > max_words:
            extended_words = words[:max_words]
            # Tiếp tục thêm từ cho đến khi gặp dấu chấm
            for word in words[max_words:]:
                extended_words.append(word)
                if word.endswith('.'):
                    break
            doan_dau = ' '.join(extended_words)
            # print(doan_dau)
        else:
            doan_dau = all_text
        if all_text.strip():
            return doan_dau, text
        else:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp"

    except Exception as e:
        return f"Sorry, đã xảy ra lỗi: {str(e)}", f"Sorry, đã xảy ra lỗi: {str(e)}"


# Stopwords để loại bỏ từ khóa nhiễu
STOPWORDS = {
    "gì", "nào", "ai", "sao", "à", "và", "là", "các", "của",
    "ấy", "thì", "ở", "đâu", "vì", "ra", "nó", "nhưng", "những", "hả", "sẽ", "mấy"
}
# Bộ mở rộng từ khóa theo loại câu hỏi
BO_TU_MO_RONG = {
    "ai": ["ai", "người", "tên", "gọi là", "ông", "bà", "cô", "chú"],
    "trong": ["ngoài", "trên", "dưới", "trong"],
    "đó là gì": ["đó là", "gọi là", "được xem là", "có nghĩa là", "định nghĩa"],
    "ở đâu": ["ở", "tại", "nơi", "địa điểm", "quê", "xuất thân"],
    "khi nào": ["khi", "năm", "tháng", "ngày", "lúc", "thời gian", "thời điểm"],
    "vì sao": ["vì", "do", "tại sao", "bởi vì", "nguyên nhân", "lý do"],
    "như thế nào": ["như", "cách", "ra sao", "mô tả", "kiểu", "dạng", "đặc điểm"],
    "bao nhiêu": ["bao nhiêu", "số", "mấy", "tổng", "khoảng"],
    "đang làm gì": ["đang làm", "hành động", "thực hiện", "công việc"],
    "phu nhân": ["phu nhân", "vợ", "bà xã"],
    "chồng": ["chồng", "ông xã", "phu quân"],
    "triều đình": ["triều đình", "vua quan", "hoàng vương", "vua chúa", "hoàng triều"],
    "ông": ["ông", "cụ", "ngài", "lão"],
    "bà": ["bà", "cô", "mợ", "thím", "chị", "dì"],
    "đình": ["đình", "đền", "miếu", "chùa", "nơi thờ"],
    "quan": ["quan", "quan lại", "quan chức", "chức tước", "viên chức"]
}


def tach_tu_khoa(text):
    """Tách từ từ văn bản và loại bỏ stopwords."""
    words = text.split()
    keywords = [
        word.lower().rstrip(".,?!")
        for word in words
        if word.lower().rstrip(".,?!") not in STOPWORDS
    ]
    return keywords if keywords else [
        word.lower().rstrip(".,?!") for word in words
    ]


def expand_keywords(base_keywords, question):
    """Mở rộng từ khóa từ câu hỏi và tách cụm từ thành từ đơn."""
    priority_keywords = []
    for key, vals in BO_TU_MO_RONG.items():
        if key in question.lower():
            priority_keywords.extend(vals)

    # Tách cụm từ thành từ đơn
    tu_don_tu_cum = []
    for cum in priority_keywords:
        tu_don_tu_cum.extend(cum.lower().split())

    # Gộp và loại trùng
    return list(set([kw.lower() for kw in base_keywords] + tu_don_tu_cum))


def xuli_doanvan_ngu_canh(user_input):
    user_keywords = tach_tu_khoa(user_input)
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


def capitalize_first_letter(paragraph):
    if len(paragraph) > 0:
        return paragraph[0].upper() + paragraph[1:]
    return paragraph


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_keyword_positions2(text, keywords):
    positions = []
    for keyword in keywords:
        # Sử dụng biểu thức chính quy để tìm từ khóa chính xác
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            positions.append(match.start())
    # print(positions)
    return sorted(positions)


def traloi_theo_ngucanh2(question, text, k=0.75):  # DÙNG CHO VĂN BẢN NHỎ
    """
    Trả lời câu hỏi từ đoạn văn bản dựa trên từ khóa mở rộng và ngữ cảnh câu.
    - question: câu hỏi
    - text: đoạn văn bản
    - k: ngưỡng tương đồng để gộp câu trùng lặp
    """
    base_keywords = tach_tu_khoa(question)
    keywords = expand_keywords(base_keywords, question)

    print(keywords)
    keyword_related_answers = {}
    y = (len(keywords)//11) + 1
    z = len(base_keywords) + len(base_keywords)//2
    print(y, z)

    # Tìm tất cả các vị trí từ khóa trong văn bản
    keyword_positions = find_keyword_positions2(text, keywords)

    for start_index in keyword_positions:
        # Tìm vị trí đầu câu (trước dấu chấm, dấu chấm than, dấu hỏi)
        sentence_start_index = max(
            text.rfind('.', 0, start_index),
            text.rfind('!', 0, start_index),
            text.rfind('?', 0, start_index)
        ) + 1
        temp_index = start_index
        while True:
            end_index = text.find(".", temp_index)
            if end_index == -1:
                break
            if end_index + 1 < len(text) and text[end_index + 1] in [' ', '\n']:
                break
            else:
                temp_index = end_index + 1
        if end_index != -1:
            related_answer = text[start_index:end_index + 1]
            related_answer1 = text[sentence_start_index:end_index + 1]
        else:
            related_answer = text[start_index:]
            related_answer1 = text[sentence_start_index:]
        words_in_related_answer = related_answer.lower().replace(
            ",", " ").rstrip(',.?!').split()

        count = sum(
            1 for word in words_in_related_answer[:z] if word in keywords)
        # Tính mật độ từ khóa trong đoạn từ từ khóa đầu đến cuối
        keyword_indices = [i for i, word in enumerate(
            words_in_related_answer) if word in keywords]
        if keyword_indices:
            keyword_span = keyword_indices[-1] - keyword_indices[0] + 1
            keyword_density = count / keyword_span if keyword_span > 0 else 0
        else:
            keyword_density = 0
        # Chỉ lưu câu trả lời nếu count > 1
        if count > y and keyword_density >= 0.1:
            related_answer1 = random.choice([related_answer1,
                                            related_answer])
            for keyword in keywords:
                if keyword in keyword_related_answers:
                    keyword_related_answers[keyword].append(
                        (related_answer1, count))
                else:
                    keyword_related_answers[keyword] = [
                        (related_answer1, count)]

    max_matched_keywords = 0
    best_related_answers = []

    for keyword, related_answers in keyword_related_answers.items():
        for related_answer, count in related_answers:
            if count > max_matched_keywords:
                max_matched_keywords = count
                best_related_answers = [related_answer]

            elif count == max_matched_keywords:
                best_related_answers.append(related_answer)

    # Lọc bỏ các câu tương tự nhau và chọn ngẫu nhiên một câu từ các câu tương tự
    groups = []
    for answer in best_related_answers:
        found_group = False

        for group in groups:
            if similar(answer, group[0]) > k:
                group.append(answer)
                found_group = True
                break

        if not found_group:
            groups.append([answer])

    # Chọn ngẫu nhiên 1 câu từ mỗi nhóm
    selected_answers = [capitalize_first_letter(
        random.choice(group)) for group in groups]
    # Xáo trộn thứ tự các câu trước khi nối chúng lại
    random.shuffle(selected_answers)
    if selected_answers:
        return ' '.join(selected_answers)
        # return restructure_response_v2(selected_answers)
        # return restructure_response_v2_1(selected_answers, keywords)
    return None


# DÙNG CHO VĂN BẢN LỚN
def traloi_theo_ngucanh1(user_input, text, similarity_threshold=0.75):
    keywords = tach_tu_khoa(user_input)
    y = (len(keywords) // 6) + 1

    def find_positions(text, delimiters):
        positions = []
        for delimiter in delimiters:
            for match in re.finditer(re.escape(delimiter), text):
                if (match.end() < len(text) and text[match.end()].isspace()) or (match.end() == len(text)):
                    if not re.match(r'\d', text[match.start() - 1:match.start()]):
                        positions.append((match.start(), delimiter))
        return positions

    def find_keyword_positions(text, keywords):
        # Tạo biểu thức chính quy kết hợp tất cả các từ khóa
        # re.escape() được sử dụng để xử lý các ký tự đặc biệt trong từ khóa
        regex_pattern = r'\b(?:' + '|'.join(re.escape(keyword)
                                            for keyword in keywords) + r')\b'

        # Sử dụng re.finditer để tìm tất cả các vị trí của từ khóa trong văn bản
        positions = [(match.start(), match.group())
                     for match in re.finditer(regex_pattern, text, re.IGNORECASE)]

        return positions

    try:
        delimiters = ['.', '!', '?']
        delimiter_positions = find_positions(text, delimiters)
        keyword_positions = find_keyword_positions(text, keywords)
        all_positions = delimiter_positions + keyword_positions
        all_positions.sort()

        best_related_answers = []
        segment_start = 0

        for pos, type in all_positions:
            if type in delimiters:
                segment = text[segment_start:pos + 1].strip()
                keyword_count = sum(keyword.lower() in re.findall(
                    r'\b\w+\b', segment.lower()) for keyword in keywords)

                # Tính toán khoảng cách trung bình giữa các từ khóa
                keyword_positions_in_segment = [
                    match.start() for keyword in keywords for match in re.finditer(r'\b{}\b'.format(re.escape(keyword)), segment.lower())
                ]
                if len(keyword_positions_in_segment) > 1:
                    avg_distance = sum(
                        abs(keyword_positions_in_segment[i] -
                            keyword_positions_in_segment[i - 1])
                        for i in range(1, len(keyword_positions_in_segment))
                    ) / (len(keyword_positions_in_segment) - 1)
                else:
                    # Nếu chỉ có 1 từ khóa, đặt khoảng cách vô cùng lớn
                    avg_distance = float('inf')

                # Chỉ thêm đoạn vào danh sách nếu khoảng cách trung bình nhỏ hơn ngưỡng
                if keyword_count > y and avg_distance < keyword_count*5:  # Đặt ngưỡng khoảng cách hợp lý
                    best_related_answers.append(
                        (segment, keyword_count, avg_distance))
                segment_start = pos + 1

                # print("kết quả đầu:  ", best_related_answers)
         # xử lý đoạn văn cuối cùng
        if segment_start < len(text):
            segment = text[segment_start:].strip()
            keyword_count = sum(keyword.lower() in re.findall(
                r'\b\w+\b', segment.lower()) for keyword in keywords)
            if keyword_count > y:
                best_related_answers.append(
                    (segment, keyword_count, avg_distance))
        # print("kết quả cuối:  ", best_related_answers)
        max_matched_keywords = 0
        filtered_answers = []
        for answer, count, avg_distance in best_related_answers:
            if count > max_matched_keywords:
                max_matched_keywords = count
                filtered_answers = [answer]
            elif count == max_matched_keywords:
                filtered_answers.append(answer)

        groups = []
        for answer in filtered_answers:
            found_group = False
            for group in groups:
                if similar(answer, group[0]) > similarity_threshold:
                    group.append(answer)
                    found_group = True
                    break
            if not found_group:
                groups.append([answer])

        selected_answers = [random.choice(group) for group in groups]
        # random.shuffle(selected_answers)

        if selected_answers:
            return ' '.join(selected_answers)
            # return restructure_response_v2(selected_answers)
            # return restructure_response_v2_1(selected_answers, keywords)

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
    return None


# DÙNG CHO VĂN BẢN LỚN
def traloi_theo_ngucanh1a(keywords, text, similarity_threshold=0.75, max_sentences=5):
    if not keywords or not text:
        return None  # Xử lý đầu vào rỗng

    y = (len(keywords) // 6) + 1  # Ngưỡng tối thiểu để chọn câu
    delimiters = ['.', '!', '?']  # Các dấu câu ngắt câu

    def split_sentences(text):
        """Tách văn bản thành từng câu dựa trên dấu ngắt câu"""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s]

    def find_keyword_positions(sentences, keywords):
        """Xác định câu nào chứa từ khóa"""
        keyword_counts = []
        for sentence in sentences:
            words = set(re.findall(r'\b\w+\b', sentence.lower()))
            count = sum(kw.lower() in words for kw in keywords)
            keyword_counts.append((sentence, count))
        return keyword_counts

    def compute_tfidf(sentences, keywords):
        """Tính toán mức độ quan trọng của câu bằng TF-IDF"""
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences + keywords)
        scores = np.mean(tfidf_matrix[:-len(keywords)].toarray(), axis=1)
        return scores

    try:
        sentences = split_sentences(text)
        keyword_positions = find_keyword_positions(sentences, keywords)

        # Lọc câu có chứa nhiều từ khóa nhất
        max_keyword_count = max(
            (count for _, count in keyword_positions), default=0)
        filtered_sentences = [
            s for s, count in keyword_positions if count == max_keyword_count]

        # Tính TF-IDF để chọn câu quan trọng nhất
        if filtered_sentences:
            tfidf_scores = compute_tfidf(filtered_sentences, keywords)
            ranked_sentences = sorted(
                zip(filtered_sentences, tfidf_scores), key=lambda x: x[1], reverse=True)
            selected_sentences = [
                s for s, _ in ranked_sentences[:max_sentences]]
        else:
            selected_sentences = []

        return ' '.join(selected_sentences) if selected_sentences else None

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None


def restructure_response_v2(selected_answers):
    if not selected_answers:
        return None

    selected_answers = [s.strip().rstrip('.') for s in selected_answers]
    n = len(selected_answers)

    if n == 1:
        return f"{selected_answers[0]}."

    elif n == 2:
        return (
            f"{selected_answers[0]}. Bên cạnh đó, {selected_answers[1].lower()}."
        )

    elif n == 3:
        return (
            f"{selected_answers[0]}. "
            f"Không những vậy, {selected_answers[1].lower()}. "
            f"Cuối cùng, {selected_answers[2].lower()}."
        )

    else:
        # Với nhiều hơn 3 đoạn, nhóm và chuyển thành đoạn tóm tắt
        intro = "Dưới đây là những điểm nổi bật:"
        bullets = "\n".join([f"- {s}." for s in selected_answers])
        return f"{intro}\n{bullets}"


def restructure_response_v2_1(selected_answers, keywords=None):
    if not selected_answers:
        return None

    selected_answers = [s.strip().rstrip('.') for s in selected_answers]
    n = len(selected_answers)

    TRANSITIONS = {
        "mở đầu": ["Trước hết", "Đầu tiên", "Thoạt tiên"],
        "bổ sung": ["Ngoài ra", "Bên cạnh đó", "Thêm vào đó"],
        "nhấn mạnh": ["Đáng chú ý là", "Đặc biệt là"],
        "kết luận": ["Cuối cùng", "Tổng kết lại", "Sau cùng"]
    }

    def pick(trans_type):
        return random.choice(TRANSITIONS.get(trans_type, [""]))

    def summarize_keywords(keywords):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np

            vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
            X = vectorizer.fit_transform(keywords)
            terms = vectorizer.get_feature_names_out()
            scores = X.toarray().sum(axis=0)
            sorted_indices = np.argsort(scores)[::-1]
            top_terms = [terms[i] for i in sorted_indices[:3]]
            return ', '.join(top_terms)
        except:
            return ', '.join(kw.split()[0] for kw in keywords[:2])

    def generate_intro(keywords):
        if not keywords:
            return ""
        topic = summarize_keywords(keywords)
        return f"Liên quan đến {topic}, dưới đây là những điểm nổi bật:"

    avg_len = sum(len(s.split()) for s in selected_answers) / n

    if n == 1:
        return f"{generate_intro(keywords)} {selected_answers[0]}."

    elif n == 2:
        return (
            f"{generate_intro(keywords)} {selected_answers[0]}. {pick('bổ sung')}, {selected_answers[1].lower()}."
        )

    elif n == 3:
        return (
            f"{generate_intro(keywords)} {pick('mở đầu')}, {selected_answers[0].lower()}. "
            f"{pick('bổ sung')}, {selected_answers[1].lower()}. "
            f"{pick('kết luận')}, {selected_answers[2].lower()}."
        )

    else:
        if avg_len <= 10:
            phrases = []
            for i, s in enumerate(selected_answers):
                if i == 0:
                    phrases.append(f"{pick('mở đầu')}, {s.lower()}")
                elif i == n - 1:
                    phrases.append(f"{pick('kết luận')}, {s.lower()}")
                else:
                    phrases.append(f"{pick('bổ sung')}, {s.lower()}")
            return f"{generate_intro(keywords)} " + ". ".join(phrases) + "."

        else:
            bullets = "\n".join([f"- {s}." for s in selected_answers])
            return f"{generate_intro(keywords)}\n{bullets}"
