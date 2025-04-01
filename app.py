import google.generativeai as genai
import schedule
import time
import threading
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, render_template
import markdown  # Thêm thư viện markdown

# Cấu hình Gemini API
GEMINI_API_KEY = "AIzaSyCVOBouQuM7Ig_YlCvmFSi9KyZr4VD8b_Y"  # Thay bằng API Key của bạn
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Cấu hình Flask
app = Flask(__name__)

# Lưu trữ lịch sử chat và kế hoạch
chat_history = []
plans = {}

# Hàm gửi email
def send_email(subject, body, to_email):
    from_email = "your_email@gmail.com"
    password = "your_password"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Hàm kiểm tra và gửi nhắc nhở
def check_reminders():
    while True:
        current_time = time.strftime("%Y-%m-%d %H:%M")
        for task, scheduled_time in plans.items():
            if current_time == scheduled_time:
                send_email("Nhắc nhở từ Gemini", f"Đã đến lúc: {task}", "your_email@gmail.com")
                chat_history.append(f"Nhắc nhở: {task} đã được gửi qua email!")
        time.sleep(60)

# Chạy lịch nhắc nhở trong luồng riêng
threading.Thread(target=check_reminders, daemon=True).start()

# Hàm gọi Gemini API
def get_gemini_response(user_input):
    try:
        response = model.generate_content(user_input)
        # Chuyển đổi Markdown thành HTML
        html_response = markdown.markdown(response.text, extensions=['extra'])
        return html_response
    except Exception as e:
        return f"Lỗi khi gọi Gemini API: {e}"

# Trang chủ với giao diện chat
@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['message']
        chat_history.append(f"Bạn: {user_input}")

        response = get_gemini_response(user_input)
        chat_history.append(f"Gemini: {response}")

        if "lên kế hoạch" in user_input.lower():
            parts = user_input.split("lúc")
            if len(parts) > 1:
                task = parts[0].replace("Lên kế hoạch", "").strip()
                schedule_time = parts[1].strip()
                plans[task] = schedule_time
                chat_history.append(f"Gemini: Đã lên kế hoạch: {task} vào {schedule_time}. Tôi sẽ nhắc bạn!")
    return render_template('chat.html', history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)