import speech_recognition
from gtts import gTTS
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os
import pygame
import re
from time import sleep

def say(robot_brain):
	tts = gTTS(text = robot_brain, lang="vi")
	# Dừng phát nhạc và giải phóng tài nguyên trước khi xóa tệp
	pygame.mixer.music.stop()
	pygame.mixer.quit()
	if os.path.exists("robot_brain.mp3"):
		os.remove("robot_brain.mp3")
	tts.save("robot_brain.mp3")
	pygame.mixer.init()
	pygame.mixer.music.load("robot_brain.mp3")
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy():
		continue

def convert(text):
	# Loại bỏ các tiêu đề (ví dụ: #, ##)
	text = re.sub(r'^#+\s', '', text, flags=re.MULTILINE)

	# Loại bỏ các ký tự đánh dấu in đậm và in nghiêng (*, **)
	text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
	text = re.sub(r'\*(.*?)\*', r'\1', text)

	# Loại bỏ tất cả các dấu *
	text = text.replace('*', '')

	# ... (thêm các quy tắc loại bỏ khác tùy thuộc vào cấu trúc Markdown) ...
	return text

def add_prompt(text):
	# Thêm prompt vào đầu văn bản
	prompt = "Bạn là một trợ lý thông minh, hãy trả lời câu hỏi của tôi một cách ngắn gọn và dễ hiểu."
	return f"{prompt}\n{text}"

def fmy_assistant():
    # Hàm này sẽ được gọi khi người dùng muốn sử dụng trợ lý ảo
    print("Trợ lý ảo đã được kích hoạt. Bạn có thể bắt đầu trò chuyện.")

    generation_config = GenerationConfig(
        temperature=0.7,
        max_output_tokens=300
    )

    # Lấy API key từ biến môi trường
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    # Cấu hình SDK với API key
    genai.configure(api_key=api_key)

    # Chọn mô hình (ví dụ: gemini-1.5-flash)
    # Bạn có thể tìm danh sách các mô hình có sẵn trong tài liệu của Google
    model = genai.GenerativeModel('gemini-1.5-flash-latest') # Hoặc 'gemini-1.0-pro', 'gemini-pro'
    chat = model.start_chat(history=[])

    robot_ear = speech_recognition.Recognizer()
    robot_brain = ""
    pygame.mixer.init()

    while True:
        with speech_recognition.Microphone() as mic:
            print("Robot: Tôi đang nghe bạn nói...")
            audio = robot_ear.listen(mic)

        try:
            you = robot_ear.recognize_google(audio, language="vi-VN")
        except:
            you = ""

        if "tắt máy tính" in you:
            robot_brain = "Em đã tắt máy tính cho anh rồi nhé."
            print("Robot: " + robot_brain)
            say(robot_brain)
            sleep(180)
            os.system("shutdown /s")
        
        elif "bye" in you or "tạm biệt" in you:
            try:
                you = add_prompt(you)
                robot_brain = chat.send_message(you, generation_config=generation_config)
                robot_brain = robot_brain.text
                robot_brain = convert(robot_brain)
            except:
                robot_brain = "Tạm biệt bạn, hẹn gặp lại lần sau."
            print("Robot: " + robot_brain)
            say(robot_brain)
            break
        elif you == "":
            robot_brain = "Tôi không nghe bạn nói, hãy thử lại."
            print("Robot: " + robot_brain)
            say(robot_brain)
        else:
            try:
                you = add_prompt(you)
                robot_brain = chat.send_message(you, generation_config=generation_config)
                robot_brain = robot_brain.text
                robot_brain = convert(robot_brain)
            except:
                robot_brain = "Tôi đang bận, vui lòng thử lại sau."

            print("Robot: " + robot_brain)

            say(robot_brain)

if __name__ == "__main__":
     fmy_assistant()