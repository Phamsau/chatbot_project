
from googlesearch import search  # Cần cài đặt: pip install googlesearch-python
from difflib import SequenceMatcher
import random
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
import time
from functools import lru_cache
from keyword_expander import tach_tu_khoa, loc_tu_quan_trong, expand_keywords, clean_text
# Lấy từ context truyền vào


def capitalize_first_letter(paragraph):
    if len(paragraph) > 0:
        return paragraph[0].upper() + paragraph[1:]
    return paragraph


@lru_cache(maxsize=10000)
def cached_similarity(a, b):
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


def luu_ngu_canh(question, answer, sources=None, context=None, MAX_QUESTIONS=5):
    if context is None:
        return

    previous_answers = context.get("previous_answers", {})

    if len(previous_answers) >= MAX_QUESTIONS:
        oldest_question = next(iter(previous_answers))
        del previous_answers[oldest_question]

    previous_answers[question] = {
        "answer": answer,
        "sources": sources or []
    }

    context["previous_answers"] = previous_answers


def xoa_ngucanh(context):
    context["previous_answers"] = {}
    return context


def xuli_doanvan_ngu_canh(context, user_input):
    user_keywords = loc_tu_quan_trong(user_input)
    print("Từ sau khi lọc bỏ và tách từ:", user_keywords)

    max_similarity = 0
    best_paragraph = None
    best_sources = []

    previous_answers = context.get("previous_answers", {})

    for previous_question, data in previous_answers.items():
        answer_text = data.get("answer", "")
        sources = data.get("sources", [])

        paragraphs = answer_text.split('\n')
        for paragraph in paragraphs:
            keywords = tach_tu_khoa(paragraph)
            common = set(user_keywords) & set(keywords)

            if not user_keywords:
                continue

            similarity = len(common) / len(user_keywords)
            if similarity > max_similarity:
                max_similarity = similarity
                best_paragraph = paragraph
                best_sources = sources

    if max_similarity >= 0.98:
        return best_paragraph.strip(), best_sources
    else:
        return None, []


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
    # Trả về phần văn bản được lấy ra từ vị trí đầu tiên của từ khóa
    return all_text


def is_valid_paragraph(text):
    if not text:
        return False
    if len(text) < 10:
        return False
    if re.match(r"^\d+[\.\)]\s", text):  # Ví dụ: "1. " hoặc "2) "
        return True
    if '.' in text or '!' in text or '?' in text:
        return True
    return False


def safe_get(url, timeout=10):
    try:
        return requests.get(url, timeout=timeout, verify=True)
    except requests.exceptions.SSLError:
        return requests.get(url, timeout=timeout, verify=False)


def search_google(keyword, user_input, context, num_of_results=5, max_sources=2, max_words=200):

    # Lọc ra từ khóa quan trọng
    keyword1 = " ".join(loc_tu_quan_trong(keyword))

    try:
        search_results = search(keyword, num_results=num_of_results, lang='vi')
        all_paragraphs = []
        used_urls = []
        sources_count = 0

        for first_link in search_results:
            if sources_count >= max_sources:
                break

            if not first_link:
                continue

            try:
                response = safe_get(first_link)

                time.sleep(random.uniform(0.3, 0.5))  # Sleep để tránh bị chặn

                soup = BeautifulSoup(response.content, 'html.parser')

                # Xoá các thẻ không mong muốn
                for tag in soup(['script', 'style', 'footer', 'header', 'nav', 'aside', 'address']):
                    tag.decompose()

                # Lấy các đoạn văn <p>, thêm separator để không dính chữ
                paragraphs = [
                    p.get_text(separator=" ", strip=True)
                    for p in soup.find_all(['p', 'div'])
                    if is_valid_paragraph(p.get_text(strip=True))
                ]

                all_paragraphs.extend(paragraphs)
                used_urls.append(first_link)
                sources_count += 1

            except requests.RequestException as e:
                # print(f"Không thể truy cập trang {first_link}: {e}")
                pass

        if not all_paragraphs:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp", []

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
        # print("đoạn văn sau khi xử lý và lưu: ", all_text, len(all_text))
        # Thêm hàm xử lý văn bản nếu có
        try:
            all_text = xuly_vanban_google(keyword, all_text)

        except:
            pass  # Nếu không có hàm này thì bỏ qua

        # Backup version xoá \n thành space
        text = all_text.replace("\n", " ")

        if text.strip():
            try:
                luu_ngu_canh(keyword, text, context=context)
            except:
                pass
        # Giới hạn số từ
        words = all_text.split()
        if len(words) > max_words:
            doan_dau_text = tra_loi_tho(user_input, text)
            if doan_dau_text:
                doan_dau = doan_dau_text
            else:
                extended_words = words[:max_words]
                # Tiếp tục thêm từ cho đến khi gặp dấu chấm
                for word in words[max_words:]:
                    extended_words.append(word)
                    if word.endswith('.'):
                        break
                doan_dau = ' '.join(extended_words)
        else:
            return text, text, used_urls
        if all_text.strip():
            return doan_dau, text, used_urls
        else:
            return "Sorry, không tìm thấy kết quả phù hợp", "Sorry, không tìm thấy kết quả phù hợp", []

    except Exception as e:
        return f"Sorry, đã xảy ra lỗi: {str(e)}", f"Sorry, đã xảy ra lỗi: {str(e)}", []


def tra_loi_tho(user_input, text):

    if len(text) >= 100000:
        best_related_answer = traloi_theo_ngucanh2_1(
            user_input, text)
        # print("đạn văn tra ngữ cảnh sll: ", best_related_answer)
    else:
        best_related_answer = traloi_theo_ngucanh2_1(
            user_input, text)
        # print("đạn văn tra ngũ cảnh sl 1000: ", best_related_answer)
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
                if cached_similarity(answer, group[0]) > similarity_threshold:
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
    print("expand_keywords: ", keywords)

    keyword_related_answers = {}
    z = max(7, (len(user_input.split()) + len(user_input.split()) // 2))
    y = 2 if ((len(keywords) // 11) + 1) < 2 else ((len(keywords) // 11) + 1)
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

        # Tách từ trong đoạn văn
        words_in_related_answer = related_answer.lower().replace(
            ",", " ").rstrip(',.?!').split()

        # ✅ Đếm mỗi từ khóa chỉ 1 lần trong z từ đầu tiên
        unique_found_keywords = set(
            word for word in words_in_related_answer[:z] if word in keywords)
        count = len(unique_found_keywords)

        # ✅ Mật độ dựa trên vị trí các từ khóa (vẫn tính như cũ)
        keyword_indices = [i for i, word in enumerate(
            words_in_related_answer) if word in keywords]
        if keyword_indices:
            span = keyword_indices[-1] - keyword_indices[0] + 1
            density = len(keyword_indices) / span if span > 0 else 0
        else:
            density = 0

        # ✅ Lọc theo ngưỡng count và mật độ
        if count >= y and density >= 0.1:
            selected_text = related_answer1 if len(related_answer1.lower().replace(
                ",", " ").rstrip(',.?!').split()) <= 50 else related_answer
            keyword_related_answers.setdefault(selected_text, count)

    # Sắp xếp theo count giảm dần
    all_related_answers = sorted(
        keyword_related_answers.items(), key=lambda x: x[1], reverse=True)

    # Lấy nhóm có count cao nhất và gần nhất
    best_related_answers = []
    if all_related_answers:
        max_matched = all_related_answers[0][1]
        best_related_answers = [
            ans for ans, c in all_related_answers if c >= max_matched - 1
        ]
    # print(best_related_answers)
    # Gom nhóm câu tương tự
    groups = []
    for ans in best_related_answers:
        found = False
        for group in groups:
            if cached_similarity(ans, group[0]) > k:
                group.append(ans)
                found = True
                break
        if not found:
            groups.append([ans])

    # Lấy 1 câu mỗi nhóm (ngẫu nhiên)
    selected_answers = [capitalize_first_letter(
        random.choice(g)) for g in groups]

    def clean_paragraph(sentences):
        text = ' '.join(sentences)
        return re.sub(r'\s+', ' ', text).strip()

    if selected_answers:
        paragraph = clean_paragraph(selected_answers)
        if len(paragraph) > 1200:
            paragraph = paragraph[:1000].rsplit(".", 1)[0] + "."
        print("sau khi lọc ngữ cảnh 2_1: ", paragraph, len(paragraph))
        return paragraph

    return None


def traloi_theo_ngucanh2_1_optimized(user_input, text, k=0.75):
    """
    Kết hợp tốc độ của bản 1 và độ chính xác lọc từ bản 2.
    Trích xuất các câu liên quan đến câu hỏi dựa trên từ khóa mở rộng và ngữ cảnh.
    """
    keywords = expand_keywords(user_input)
    keyword_related_answers = {}

    # Giữ nguyên cách tính như bản 2
    z = 5 if len(keywords) <= 3 else (
        len(keywords) + len(keywords) // 2)
    y = 2 if ((len(keywords) // 11) + 1) < 2 else ((len(keywords) // 11) + 1)

    print("Ngưỡng count:", y, "| Số từ lấy để đếm:", z)

    keyword_positions = find_keyword_positions2(text, keywords)

    for start_index in keyword_positions:
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
            temp_index = end_index + 1

        related_answer = text[start_index:end_index +
                              1] if end_index != -1 else text[start_index:]
        related_answer1 = text[sentence_start_index:end_index +
                               1] if end_index != -1 else text[sentence_start_index:]

        # Tính count và density
        words_in_related_answer = related_answer.lower().replace(
            ",", " ").rstrip(',.?!').split()
        count = sum(
            1 for word in words_in_related_answer[:z] if word in keywords)
        # print(related_answer, count)
        keyword_indices = [i for i, word in enumerate(
            words_in_related_answer) if word in keywords]
        if keyword_indices:
            span = keyword_indices[-1] - keyword_indices[0] + 1
            density = len(keyword_indices) / span if span > 0 else 0
        else:
            density = 0

        # Lọc theo ngưỡng
        if count >= y and density >= 0.1:
            selected_text = related_answer1.strip()
            # Chỉ lưu 1 lần mỗi đoạn
            keyword_related_answers[selected_text] = count
        # print(keyword_related_answers, count)
    # Lấy những đoạn có count gần max
    all_related_answers = list(keyword_related_answers.items())
    best_related_answers = []
    if all_related_answers:
        max_matched = max(c for _, c in all_related_answers)
        best_related_answers = [
            ans for ans, c in all_related_answers if c >= max_matched - 1
        ]

    # Gom nhóm đoạn tương tự
    groups = []
    for ans in best_related_answers:
        found = False
        for group in groups:
            if cached_similarity(ans, group[0]) > k:
                group.append(ans)
                found = True
                break
        if not found:
            groups.append([ans])

    # Lấy mỗi nhóm một đoạn
    selected_answers = [capitalize_first_letter(
        random.choice(g)) for g in groups]

    def clean_paragraph(sentences):
        text = ' '.join(sentences)
        return re.sub(r'\s+', ' ', text).strip()

    if selected_answers:
        paragraph = clean_paragraph(selected_answers)
        if len(paragraph) > 2000:
            paragraph = paragraph[:1000].rsplit(".", 1)[0] + "."
        # print("✔️ Đoạn trích ngữ cảnh:", paragraph, len(paragraph))
        return paragraph

    return None


def traloi_theo_ngucanh2_1_thu(user_input, text, k=0.75):
    keywords = set(expand_keywords(user_input))
    base_keywords = set(tach_tu_khoa(user_input))

    z = 5 if len(base_keywords) <= 3 else len(
        base_keywords) + len(base_keywords) // 2
    y = max((len(keywords) // 11) + 1, 2)

    print("Ngưỡng count:", y, "| Số từ lấy để đếm:", z)

    # Tìm tất cả câu trước
    sentences = re.split(r'(?<=[.?!])\s+', text)
    keyword_related_answers = {}

    for sent in sentences:
        lowered = sent.lower()
        words = re.findall(r'\w+', lowered)
        count = sum(1 for word in words[:z] if word in keywords)

        # Tính mật độ tập trung
        keyword_indices = [i for i, word in enumerate(
            words) if word in keywords]
        if keyword_indices:
            span = keyword_indices[-1] - keyword_indices[0] + 1
            density = len(keyword_indices) / span if span > 0 else 0
        else:
            density = 0

        if count >= y and density >= 0.1:
            clean_sent = sent.strip()
            keyword_related_answers[clean_sent] = count
            # print("✔️", clean_sent[:60], "...", "| Count:", count)

    if not keyword_related_answers:
        return None

    # Lấy top đoạn gần max count
    all_related = list(keyword_related_answers.items())
    max_count = max(c for _, c in all_related)
    best_related = [ans for ans, c in all_related if c >= max_count - 1]

    # Gom nhóm bằng hash trước để tránh trùng
    seen = set()
    selected = []
    for s in best_related:
        h = hash(s.lower())
        if h not in seen:
            seen.add(h)
            selected.append(s)

    # Gộp đoạn kết quả
    paragraph = ' '.join(capitalize_first_letter(s) for s in selected)
    if len(paragraph) > 2000:
        paragraph = paragraph[:1000].rsplit(".", 1)[0] + "."
    # print("✔️ Đoạn trích ngữ cảnh (tối ưu):",
    #       paragraph)
    return paragraph
