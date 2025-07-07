
from playsound import playsound
import asyncio
import time
import platform
import edge_tts
from gtts import gTTS
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.playback import play


def recognize_speech():
    # Khởi tạo một đối tượng recognizer
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Nghe...")
        audio = r.listen(source)
    try:
        print("Đang nhận dạng...")
        # Chuyển đổi giọng nói thành văn bản tiếng Việt
        text = r.recognize_google(audio, language="vi-VN")
        print("User: ", text)
        return text
    except sr.UnknownValueError:
        print("Không nhận dạng được giọng nói.")
        return ""
    except sr.RequestError as e:
        print("Lỗi trong quá trình nhận dạng giọng nói: {0}".format(e))
        return ""


def recognize_speech1():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # print("🔊 Đang điều chỉnh nhiễu môi trường...")
        r.adjust_for_ambient_noise(source, duration=1)
        print("🎙️ Nghe...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("⌛ Không nghe thấy gì sau 5 giây.")
            return ""

    try:
        # print("🧠 Đang nhận dạng...")
        text = r.recognize_google(audio, language="vi-VN")
        print("👤 Bạn:", text)
        return text
    except sr.UnknownValueError:
        print("⚠️ Không hiểu bạn nói gì.")
        return ""
    except sr.RequestError as e:
        print("❌ Lỗi kết nối nhận dạng:", e)
        return ""


def speak_text(text):
    # Xóa tệp âm thanh cũ nếu tồn tại
    if os.path.exists('output.mp3'):
        os.remove('output.mp3')
    tts = gTTS(text=text, lang='vi', slow=False)
    tts.save('output.mp3')
    # Mở tệp MP3
    audio = AudioSegment.from_mp3("output.mp3")
    play(audio)
    # Xóa tệp âm thanh sau khi phát xong
    os.remove('output.mp3')


# "vi-VN-HoaiMyNeural" giọng nữ, vi-VN-NamMinhNeural giọng nam
def speak_text1(text, voice="vi-VN-NamMinhNeural", rate="+10%"):
    async def run():
        output_file = "output.mp3"
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        await communicate.save(output_file)

        # Đọc và phát file bằng pydub
        try:
            sound = AudioSegment.from_file(output_file, format="mp3")
            play(sound)
        except Exception as e:
            print("🔇 Không thể phát âm thanh:", e)

        # Xóa file sau khi phát
        if os.path.exists(output_file):
            os.remove(output_file)

    asyncio.run(run())
