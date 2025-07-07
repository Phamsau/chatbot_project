import requests
from gtts import gTTS
import time
import os
import speech_recognition as sr
from datetime import datetime
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
        print("Đã nhận dạng:", text)
        return text
    except sr.UnknownValueError:
        print("Không nhận dạng được giọng nói.")
        return ""
    except sr.RequestError as e:
        print("Lỗi trong quá trình nhận dạng giọng nói: {0}".format(e))
        return ""


def speak_text(text):
    # Xóa tệp âm thanh cũ nếu tồn tại
    if os.path.exists('output.mp3'):
        os.remove('output.mp3')

    tts = gTTS(text=text, lang='vi', slow=False)
    tts.save('output.mp3')

    # Mở và phát tệp âm thanh
   # Mở tệp MP3

    audio = AudioSegment.from_mp3("output.mp3")
    play(audio)

    # Xóa tệp âm thanh sau khi phát xong
    os.remove('output.mp3')


def get_weather(city):
    # Thay YOUR_API_KEY bằng API key của bạn từ OpenWeatherMap
    api_key = '0c4060431c9a2b2ade657c250e67ebe4'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {'q': city, 'appid': api_key, 'units': 'metric'}
    response = requests.get(base_url, params=params)
    data = response.json()

    if data['cod'] == '404':
        return 'Không tìm thấy thông tin thời tiết cho thành phố/tỉnh này.'

    city_name = data['name']
    weather_main = data['weather'][0]['main']
    weather_desc = data['weather'][0]['description']
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    pressure = data['main']['pressure']

    # Kiểm tra điều kiện có mưa hay nắng
    if 'mưa' in weather_desc.lower() or 'mưa' in weather_main.lower():
        weather_info = f'Thời tiết tại {city_name} ngày {datetime.now().strftime("%d/%m/%Y")}: Có mưa\n'
    elif 'nắng' in weather_desc.lower() or 'nắng' in weather_main.lower():
        weather_info = f'Thời tiết tại {city_name} ngày {datetime.now().strftime("%d/%m/%Y")}: Có nắng\n'
    else:
        weather_info = f'Thời tiết tại {city_name} ngày {datetime.now().strftime("%d/%m/%Y")}: {weather_desc}\n'

    weather_info += f'Tình trạng: {weather_main}\n' \
                    f'Nhiệt độ: {temp}°C\n' \
                    f'Độ ẩm: {humidity}%\n' \
                    f'Tốc độ gió: {wind_speed} m/s\n' \
                    f'Áp suất: {pressure} hPa'

    return weather_info


# Sử dụng chương trình
speak_text("bạn muốn biết thông tin thời tiết của tỉnh thành nào?")
city = recognize_speech().strip().replace('\n', '')
weather = get_weather(city)
speak_text(weather)
print("[PRINT]"+weather)
