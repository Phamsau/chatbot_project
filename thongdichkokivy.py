from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS
import os
import sys
from pydub import AudioSegment
from pydub.playback import play


def translate_text(text, src_lang, dest_lang):
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, src=src_lang, dest=dest_lang)
    return translation.text


def speech_to_text(language='en-US'):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Lắng nghe trong khoảng thời gian ngắn
        audio = recognizer.listen(source, timeout=10)

    try:
        text = recognizer.recognize_google(
            audio, language='vi-VN')  # Nhận dạng tiếng Việt
        return text
    except sr.UnknownValueError:
        pass

    try:
        text = recognizer.recognize_google(
            audio, language='en-US')  # Nhận dạng tiếng Anh
        return text
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("Lỗi trong quá trình nhận dạng giọng nói: {0}".format(e))

    return ""


def speech_to_text1(preferred_languages=('vi-VN', 'en-US'), timeout=10, noise_duration=1):
    """
    Nhận dạng giọng nói, thử các ngôn ngữ trong preferred_languages.
    Có lọc nhiễu môi trường.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🔧 Đang điều chỉnh tiếng ồn môi trường...")
        recognizer.adjust_for_ambient_noise(source, duration=noise_duration)

        print("🎙️ Đang lắng nghe...")
        try:
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            print("⌛ Không phát hiện giọng nói.")
            return ""

    for lang in preferred_languages:
        try:
            print(f"🧠 Đang nhận dạng ({lang})...")
            text = recognizer.recognize_google(audio, language=lang)
            print(f"📥 Bạn ({lang}):", text)
            return text
        except sr.UnknownValueError:
            print(f"❓ Không hiểu ({lang})...")
        except sr.RequestError as e:
            print(f"❌ Lỗi kết nối ({lang}): {e}")
            break

    return ""


def speak_text(text, lang):
    # Xóa tệp âm thanh cũ nếu tồn tại
    if os.path.exists('output.mp3'):
        os.remove('output.mp3')

    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save('output.mp3')

    # Mở và phát tệp âm thanh
   # Mở tệp MP3

    audio = AudioSegment.from_mp3("output.mp3")
    play(audio)

    # Xóa tệp âm thanh sau khi phát xong
    os.remove('output.mp3')


def text_to_speech(text, lang):
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, dest=lang)
    return translation.text


def detect_language(text):
    if text is None or text == "":
        return ""  # Trả về chuỗi rỗng nếu không có văn bản để nhận dạng ngôn ngữ

    translator = Translator(service_urls=['translate.google.com'])
    detected = translator.detect(text)

    if detected is not None and hasattr(detected, "lang"):
        return detected.lang
    else:
        return ""  # Trả về chuỗi rỗng nếu không nhận dạng được ngôn ngữ


def main():
    running = True
    while running:
        print("Hãy nói gì đó...")
        text = speech_to_text1()

        if text == "":
            print("Không nhận được giọng nói, bạn muốn: TIẾP TỤC hay DỪNG LẠI ?")
            speak_text(
                "Không nhận được giọng nói, bạn muốn TIẾP TỤC phiên dịch hay DỪNG LẠI ?", lang='vi')
            print("nghe...")
            key = speech_to_text1()

            if key == "":
                running = False
                speak_text(
                    "kết thúc chương trình phiên dịch, hẹn gặp lại", lang='vi')
                sys.exit("Thoát chương trình.")
            elif key == "dừng lại":
                running = False
                speak_text(
                    "kết thúc chương trình phiên dịch, hẹn gặp lại", lang='vi')
                sys.exit("Thoát chương trình.")
            else:
                speak_text(
                    "ok, chương trình phiên dịch được tiếp tục", lang='vi')
        else:
            lang = detect_language(text)

            if lang == 'en':
                translated_text = translate_text(text, 'en', 'vi')
                print("Đoạn văn bản tiếng Việt: ", translated_text)
                speak_text(translated_text, lang='vi')
            elif lang == 'vi':
                translated_text = translate_text(text, 'vi', 'en')
                print("Đoạn văn bản tiếng Anh: ", translated_text)
                speak_text(translated_text, lang='en')
            else:
                print("Không nhận diện được ngôn ngữ.")
    return ""


if __name__ == "__main__":
    main()
