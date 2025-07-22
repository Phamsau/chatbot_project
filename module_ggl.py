
from googlesearch import search  # Cần cài đặt: pip install googlesearch-python
import numpy as np
from difflib import SequenceMatcher
import random
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
import time
previous_answers = {}

# Stopwords để loại bỏ từ khóa nhiễu
STOPWORDS = {
    "gì", "nào", "ai", "sao", "à", "và", "là", "các",
    "ấy", "thì", "ở", "đâu", "vì", "ra", "nó", "nhưng", "những", "hả", "sẽ", "mấy", "không"
}
STOP_PHRASES = [
    "bao nhiêu", "như thế nào", "làm sao", "ở đâu", "khi nào", "là gì", "tại sao", "vì sao", "tại vì sao",
    "ai là", "ai đã", "ai đang", "có đúng không", "có phải là", "có thể", "có hay không", "có không",
    "nào là", "cái gì", "gì vậy", "thế nào", "cách nào", "phải không", "ra sao", "để làm gì",
    "mấy giờ", "mấy tuổi", "bao nhiêu", "kéo dài bao lâu",
    "bằng cách nào", "vì điều gì", "có nghĩa là gì", "được không", "được chứ", "bạn có biết", "là gì", "là ai", "có biết"
]
# Bộ mở rộng từ khóa theo loại câu hỏi
BO_TU_MO_RONG = {
    "trong": ["ngoài", "trên", "dưới", "trong"],
    "đó là gì": ["đó là", "gọi là", "được xem là", "đây là"],
    "ở đâu": ["ở", "tại", "nơi", "địa điểm", "quê", "xuất thân"],
    "khi nào": ["khi", "năm", "tháng", "ngày", "lúc", "thời gian", "thời điểm"],
    "vì sao": ["vì", "do", "tại vì", "bởi vì", "nguyên nhân", "lý do"],
    "như thế nào": ["như thế này", "cách", "ra sao", "mô tả", "kiểu", "dạng", "đặc điểm"],
    "bao nhiêu": ["số", "tổng", "khoảng" "chừng"],
    "đang làm gì": ["đang làm", "hành động", "thực hiện", "công việc"],
    "phu nhân": ["phu nhân", "vợ"],
    "chồng": ["chồng", "phu quân"],
    "triều đình": ["triều đình", "vua quan", "hoàng vương", "vua chúa", "hoàng triều"],
    "ông": ["ông", "cụ", "ngài", "lão"],
    "bà": ["bà", "cô", "mợ", "thím", "chị", "dì"],
    "đình": ["đình", "đền", "miếu", "chùa", "nơi thờ"],
    "quan": ["quan", "quan lại", "quan chức", "chức tước", "viên chức"],
    "quê": ["quê", "quán", "nơi sinh", "sinh sống", "hiện ở tại"],
    "chết": ["chết", "mất", "tử vong", "qua đời"]
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


def loc_tu_quan_trong(cau_hoi):
    cau_hoi = cau_hoi.lower()
    cau_hoi = re.sub(r"[^\w\s]", "", cau_hoi)  # loại bỏ dấu câu

    # Loại các cụm stop phrases trước
    for phrase in STOP_PHRASES:
        cau_hoi = cau_hoi.replace(phrase, "")

    # Tách từ và loại bỏ stopwords đơn lẻ
    words = cau_hoi.split()
    return [w for w in words if w not in STOPWORDS]


def expand_keywords(question):
    """Mở rộng từ khóa theo loại câu hỏi dựa trên các cụm từ ưu tiên đã định nghĩa."""
    base_keywords = tach_tu_khoa(question)
    question_lower = question.lower()
    priority_keywords = []
    for nhom, cum_tu in BO_TU_MO_RONG.items():
        for phrase in cum_tu:
            if phrase in question_lower:
                priority_keywords.extend(cum_tu)
                # break  # Nếu một cụm phù hợp thì thêm toàn bộ nhóm

    # Tách cụm từ thành từ đơn
    tu_don_tu_cum = []
    for cum in priority_keywords:
        tu_don_tu_cum.extend(cum.lower().split())

    # Gộp và loại trùng
    return list(set([kw.lower() for kw in base_keywords] + tu_don_tu_cum))


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


def luu_ngu_canh(question, answer, MAX_QUESTIONS=5):
    if len(previous_answers) >= MAX_QUESTIONS:
        oldest_question = next(iter(previous_answers))  # Lấy câu hỏi cũ nhất
        del previous_answers[oldest_question]  # Xóa câu hỏi cũ nhất
    # Lưu câu hỏi và câu trả lời mới vào từ điển
    previous_answers[question] = answer
    return previous_answers


def xoa_ngucanh():
    return previous_answers.clear()


def xuli_doanvan_ngu_canh(user_input):
    user_keywords = loc_tu_quan_trong(user_input)
    print("từ sau khi lọc bỏ và tách từ: ", user_keywords)
    max_similarity = 0
    best_paragraph = None

    for previous_question, previous_answer in previous_answers.items():
        paragraphs = previous_answer.split('\n')

        for paragraph in paragraphs:
            keywords = tach_tu_khoa(paragraph)
            common = set(user_keywords) & set(keywords)

            if not user_keywords:
                continue  # tránh chia 0

            similarity = len(common) / len(user_keywords)

            if similarity > max_similarity:
                max_similarity = similarity
                best_paragraph = paragraph

    if max_similarity >= 0.9:
        print("đoạn  văn lọc được: ", best_paragraph.strip())
        return best_paragraph.strip()
    else:
        return None


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


def search_google(keyword, num_of_results=5, max_sources=2, max_words=200):

    keyword = " ".join(loc_tu_quan_trong(keyword))

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
                time.sleep(random.uniform(0.3, 0.5))  # Sleep để tránh bị chặn

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
            doan_dau_text = tra_loi_tho(keyword, text)
            if doan_dau_text:

                doan_dau = doan_dau_text
            else:
                doan_dau = f"Xin lỗi, tôi không tìm thấy thông tin {keyword}"
                print("đạn văn seachgoogle sl 200: ", doan_dau)
        else:
            doan_dau = all_text
        if all_text.strip():
            return doan_dau, text
        else:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp"

    except Exception as e:
        return f"Sorry, đã xảy ra lỗi: {str(e)}", f"Sorry, đã xảy ra lỗi: {str(e)}"


def tra_loi_tho(user_input, text):

    if len(text) >= 100000:
        best_related_answer = traloi_theo_ngucanh1(user_input, text)
        print("đạn văn seachgoogle sll: ", best_related_answer)
    else:
        best_related_answer = traloi_theo_ngucanh2_1(user_input, text)
        print("đạn văn seachgoogle sl 1000: ", best_related_answer)
    return best_related_answer

# DÙNG CHO VĂN BẢN LỚN


def traloi_theo_ngucanh1(user_input, text, similarity_threshold=0.75):

    keywords = expand_keywords(user_input)
    y = (len(keywords) // 11) + 1

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


def traloi_theo_ngucanh2_1(user_input, text, k=0.75):
    """
    Trích xuất các câu liên quan đến câu hỏi dựa trên từ khóa mở rộng và ngữ cảnh.
    - Trả về đoạn văn ngắn gọn, cô đọng, sẵn sàng làm đầu vào cho LLM.
    """
    keywords = expand_keywords(user_input)
    print(keywords)

    keyword_related_answers = {}
    y = (len(keywords) // 11) + 1
    z = len(tach_tu_khoa(user_input)) + len(tach_tu_khoa(user_input))//2
    print("Ngưỡng count:", y, "| Số từ lấy để đếm:", z)

    keyword_positions = find_keyword_positions2(text, keywords)

    for start_index in keyword_positions:
        # Tìm đầu câu
        sentence_start_index = max(
            text.rfind('.', 0, start_index),
            text.rfind('!', 0, start_index),
            text.rfind('?', 0, start_index)
        ) + 1

        # Tìm cuối câu
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

        # Tính count và density
        words_in_related_answer = related_answer.lower().replace(
            ",", " ").rstrip(',.?!').split()
        count = sum(
            1 for word in words_in_related_answer[:z] if word in keywords)
        keyword_indices = [i for i, word in enumerate(
            words_in_related_answer) if word in keywords]
        if keyword_indices:
            span = keyword_indices[-1] - keyword_indices[0] + 1
            density = count / span if span > 0 else 0
        else:
            density = 0

        # Lọc theo ngưỡng
        if count > y and density >= 0.1:
            selected_text = related_answer1
            for kw in keywords:
                if kw in keyword_related_answers:
                    keyword_related_answers[kw].append((selected_text, count))
                else:
                    keyword_related_answers[kw] = [(selected_text, count)]

    # Gom tất cả đoạn và đếm max
    all_related_answers = []
    for related_list in keyword_related_answers.values():
        all_related_answers.extend(related_list)

    best_related_answers = []
    if all_related_answers:
        max_matched = max(c for _, c in all_related_answers)
        best_related_answers = [
            ans for ans, c in all_related_answers
            if c >= max_matched - 1  # Lấy cả nhóm sát bên dưới
        ]

    # Lọc trùng theo độ tương đồng
    groups = []
    for ans in best_related_answers:
        found = False
        for group in groups:
            if similar(ans, group[0]) > k:
                group.append(ans)
                found = True
                break
        if not found:
            groups.append([ans])

    # Lấy ngẫu nhiên 1 câu mỗi nhóm
    selected_answers = [capitalize_first_letter(
        random.choice(g)) for g in groups]

    # Xáo và nối lại thành đoạn văn mạch
    def clean_paragraph(sentences):
        text = ' '.join(sentences)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    if selected_answers:

        paragraph = clean_paragraph(selected_answers)  # Không shuffle
        if len(paragraph) > 2000:
            paragraph = paragraph[:1000].rsplit(".", 1)[0] + "."
        return paragraph
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
