
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


def search_google(keyword, num_of_results=10, max_sources=2, max_words=100):
    try:
        search_results = search(keyword, num_results=num_of_results, lang='vi')
        all_paragraphs = []  # Danh sách để lưu trữ các đoạn văn từ tất cả các nguồn
        sources_count = 0     # Đếm số lượng nguồn đã xử lý

        for first_link in search_results:
            if sources_count >= max_sources:
                break  # Dừng lại nếu đã xử lý đủ số lượng nguồn

            if first_link:
                try:
                    page = requests.get(first_link, verify=False)
                    time.sleep(random.uniform(1, 3))

                    soup = BeautifulSoup(page.content, 'html.parser')

                    # Loại bỏ các thẻ không mong muốn
                    for tag in soup(['script', 'style', 'footer', 'header', 'nav', 'aside', 'address']):
                        tag.extract()

                    paragraphs = [paragraph.get_text()
                                  for paragraph in soup.find_all('p')]

                    # Thêm các đoạn văn của mỗi nguồn vào danh sách chung
                    all_paragraphs.extend(paragraphs)
                    sources_count += 1  # Tăng số lượng nguồn đã xử lý

                except requests.RequestException as e:
                    print(f"Không thể truy cập trang {first_link}: {e}")

        if not all_paragraphs:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp"

        # Kết hợp tất cả các đoạn văn từ các nguồn lại với nhau
        all_text = '\n'.join(filter(None, all_paragraphs))

        # Các bước làm sạch văn bản
        all_text = re.sub(
            r'Hãy xác nhận rằng quý vị là chuyên gia chăm sóc sức khỏe|Liên kết bạn vừa chọn sẽ đưa bạn tới trang web của một bên thứ ba\. Chúng tôi không kiểm soát hay có trách nhiệm đối với nội dung trang web của bất kỳ bên thứ ba nào\. Nhập cụm từ tìm kiếm để tìm các chủ đề, nội dung đa phương tiện và nhiều nội dung khác về y tế có liên quan\.',
            '',
            all_text
        )
        all_text = re.sub(r'\(.*?\)|\[.*?\]|\|.*?\||[_*|()]', '', all_text)
        all_text = xuly_vanban_google(keyword, all_text)
        # The code is replacing all occurrences of newline characters ("\n") in the variable
        # `all_text` with a space character.
        k = all_text.replace("\n", " ")
        # print(len(k))

        if k.strip():
            luu_ngu_canh(keyword, k)

        # Giới hạn số từ trích xuất nếu vượt quá `max_words`
        words = all_text.split()
        if len(words) > max_words:
            words = words[:max_words]
            all_text = ' '.join(words)

        # Xóa các đoạn văn bản không mong muốn
        text_to_remove = (
            r'Liên kết bạn vừa chọn sẽ đưa bạn tới trang web của một bên thứ ba\. '
            r'Chúng tôi không kiểm soát hay có trách nhiệm đối với nội dung trang web của bất kỳ bên thứ ba nào\. '
            r'Nhập cụm từ tìm kiếm để tìm các chủ đề, nội dung đa phương tiện và nhiều nội dung khác về y tế có liên quan\.'
            r' • Sử dụng "" để tìm cả cụm chính xác o • Sử dụng – để loại bỏ kết quả chứa cụm từ nhất định o'
            r' • Sử dụng OR để cho biết cụm từ thay thế o Theo , MD, Sidney Kimmel Medical College at Thomas Jefferson University'
        )
        all_text = re.sub(text_to_remove, '', all_text)

        if all_text.strip():
            return all_text, k
        else:
            all_text = k1 = "Sorry, không tìm thấy kết quả phù hợp"
    except Exception as e:
        all_text = k = f"Sorry, đã xảy ra lỗi: {str(e)}"
    return all_text, k


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
                print(f"Không thể truy cập trang {first_link}: {e}")

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
        k = all_text.replace("\n", " ")

        if k.strip():
            try:
                luu_ngu_canh(keyword, k)
            except:
                pass

        # Giới hạn số từ
        words = all_text.split()
        if len(words) > max_words:
            words = words[:max_words]
            all_text = ' '.join(words)

        if all_text.strip():
            return all_text, k
        else:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp"

    except Exception as e:
        return f"Sorry, đã xảy ra lỗi: {str(e)}", f"Sorry, đã xảy ra lỗi: {str(e)}"


def search_google_2(keyword, num_of_results=10, max_sources=2, max_words=100):
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
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                }
                response = requests.get(
                    first_link, timeout=10, headers=headers, verify=False)
                time.sleep(random.uniform(1, 3))

                soup = BeautifulSoup(response.content, 'html.parser')

                # Xóa các thẻ không cần thiết
                for tag in soup(['script', 'style', 'footer', 'header', 'nav', 'aside', 'address', 'noscript', 'form']):
                    tag.decompose()

                # Lấy các đoạn văn bản và lọc rác
                paragraphs = [
                    p.get_text(separator=" ", strip=True)
                    for p in soup.find_all('p')
                    if len(p.get_text(strip=True)) > 20 and not re.search(r'cookie|chính sách|quảng cáo|bản quyền|đăng nhập|http', p.get_text().lower())
                ]

                # Nếu nội dung có đủ giá trị, thêm vào
                if sum(len(p.split()) for p in paragraphs) >= 30:
                    all_paragraphs.extend(paragraphs)
                    sources_count += 1

            except requests.RequestException as e:
                print(f"Không thể truy cập trang {first_link}: {e}")

        if not all_paragraphs:
            return "Không tìm thấy nội dung phù hợp.", "Không tìm thấy nội dung phù hợp."

        # Kết hợp văn bản
        all_text = '\n'.join(filter(None, all_paragraphs))

        # Làm sạch văn bản
        all_text = re.sub(r'\s+', ' ', all_text)
        all_text = re.sub(r'\s+([.,;!?])', r'\1', all_text)
        all_text = re.sub(r'([.,!?])([^\s])', r'\1 \2', all_text)

        # Loại bỏ các mẫu rác
        patterns_to_remove = [
            r'Hãy xác nhận rằng.*?chăm sóc sức khỏe',
            r'Liên kết bạn vừa chọn.*?liên quan\.',
            r'Trình duyệt của bạn.*?không hỗ trợ',
            r'Truy cập trang web chính thức.*?',
            r'This site uses cookies.*?',
            r'Chúng tôi sử dụng cookie.*?',
            r'\(.*?\)', r'\[.*?\]', r'\|.*?\|', r'[_*|()]'
        ]
        for pattern in patterns_to_remove:
            all_text = re.sub(pattern, '', all_text, flags=re.DOTALL)

        # Viết hoa đầu câu, chuẩn hóa chấm câu
        sentences = re.split(r'(?<=[.!?])\s+', all_text)
        sentences = [s.strip().capitalize() for s in sentences if s.strip()]
        all_text = '. '.join(sentences)

        # Xử lý bằng hàm ngoài nếu có
        try:
            all_text = xuly_vanban_google(keyword, all_text)
        except:
            pass

        # Bản không chứa dấu xuống dòng
        k = all_text.replace("\n", " ")

        # Lưu nếu cần
        try:
            if k.strip():
                luu_ngu_canh(keyword, k)
        except:
            pass

        # Giới hạn số từ
        words = all_text.split()
        if len(words) > max_words:
            all_text = ' '.join(words[:max_words])

        return all_text, k

    except Exception as e:
        return f"Đã xảy ra lỗi: {str(e)}", f"Đã xảy ra lỗi: {str(e)}"


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


def traloi_theo_ngucanh2(keywords, text, k=0.75):
    keyword_related_answers = {}
    y = (len(keywords)//6) + 1
    z = len(keywords) + len(keywords)//2

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
        # Chỉ lưu câu trả lời nếu count > 1
        if count > y:
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
        # return ' '.join(selected_answers)
        return restructure_response_v2(selected_answers)
        # return restructure_response_v2_1(selected_answers, keywords)
    return None


def traloi_theo_ngucanh1(keywords, text, similarity_threshold=0.75):

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
            # return ' '.join(selected_answers)
            return restructure_response_v2(selected_answers)
            # return restructure_response_v2_1(selected_answers, keywords)

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
    return None


def traloi_theo_ngucanh1b(keywords, text, similarity_threshold=0.75, max_sentences=5):
    if not keywords or not text:
        return None  # Xử lý đầu vào rỗng

    y = (len(keywords) // 6) + 1

    def find_positions(text, delimiters):
        positions = []
        for delimiter in delimiters:
            for match in re.finditer(re.escape(delimiter), text):
                if match.end() == len(text) or text[match.end()].isspace():
                    if match.start() > 0 and not re.match(r'\d', text[match.start() - 1]):
                        positions.append((match.start(), delimiter))
        return positions

    def find_keyword_positions(text, keywords):
        regex_pattern = r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b'
        return [(match.start(), match.group()) for match in re.finditer(regex_pattern, text, re.IGNORECASE)]

    try:
        delimiters = ['.', '!', '?']
        delimiter_positions = find_positions(text, delimiters)
        keyword_positions = find_keyword_positions(text, keywords)

        all_positions = sorted(delimiter_positions + keyword_positions)
        best_related_answers = []
        segment_start = 0

        for pos, typ in all_positions:
            if typ in delimiters:
                segment = text[segment_start:pos + 1].strip()
                words_in_segment = set(re.findall(r'\b\w+\b', segment.lower()))
                keyword_count = sum(
                    kw.lower() in words_in_segment for kw in keywords)

                keyword_positions_in_segment = [
                    match.start() for kw in keywords
                    for match in re.finditer(r'\b{}\b'.format(re.escape(kw)), segment.lower())
                ]

                avg_distance = (
                    sum(abs(keyword_positions_in_segment[i] - keyword_positions_in_segment[i - 1])
                        for i in range(1, len(keyword_positions_in_segment))) / (len(keyword_positions_in_segment) - 1)
                ) if len(keyword_positions_in_segment) > 1 else float('inf')

                if keyword_count > y and avg_distance < keyword_count * 5:
                    best_related_answers.append(
                        (segment, keyword_count, avg_distance))

                segment_start = pos + 1

        if segment_start < len(text):
            segment = text[segment_start:].strip()
            words_in_segment = set(re.findall(r'\b\w+\b', segment.lower()))
            keyword_count = sum(
                kw.lower() in words_in_segment for kw in keywords)
            if keyword_count > y:
                best_related_answers.append(
                    (segment, keyword_count, float('inf')))

        max_matched_keywords = max(
            (count for _, count, _ in best_related_answers), default=0)
        filtered_answers = [
            ans for ans, count, _ in best_related_answers if count == max_matched_keywords]

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
        random.shuffle(selected_answers)

        return ' '.join(selected_answers[:max_sentences]) if selected_answers else None

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        return None


def traloi_theo_ngucanh1c(keywords, text, similarity_threshold=0.75, max_sentences=5):
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


def tach_tu_khoa_tu_cau_hoi(question):
    # Loại bỏ dấu câu và tách từ
    words = re.findall(r'\b\w+\b', question.lower())
    # Từ dừng đơn giản (có thể mở rộng thêm)
    stopwords = {'what', 'is', 'are', 'the', 'of', 'a',
                 'an', 'for', 'to', 'why', 'how', 'do', 'does', 'did'}
    keywords = [w for w in words if w not in stopwords]
    return keywords


def traloi_theo_ngucanh2c(keywords, text, similarity_threshold=0.75, max_sentences=5):

    def split_sentences(text):
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s]

    def find_keyword_positions(sentences, keywords):
        keyword_counts = []
        for sentence in sentences:
            words = set(re.findall(r'\b\w+\b', sentence.lower()))
            count = sum(kw.lower() in words for kw in keywords)
            keyword_counts.append((sentence, count))
        return keyword_counts

    def compute_tfidf(sentences, keywords):
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences + keywords)
        scores = np.mean(tfidf_matrix[:-len(keywords)].toarray(), axis=1)
        return scores

    try:
        sentences = split_sentences(text)
        keyword_positions = find_keyword_positions(sentences, keywords)

        max_keyword_count = max(
            (count for _, count in keyword_positions), default=0)
        filtered_sentences = [
            s for s, count in keyword_positions if count == max_keyword_count]

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


def capitalize_first_letter(paragraph):
    if len(paragraph) > 0:
        return paragraph[0].upper() + paragraph[1:]
    return paragraph
