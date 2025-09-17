from easysnmp import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

list_ip = [
    "11.57.143.22",
    "11.57.143.23",
    "11.54.149.11",
    "11.61.144.71",
    "11.61.144.72"
]

OIDS = {
    "Enatel": ("iso.3.6.1.4.1.21940.2.4.2.24.0", 1),     
    "Delta":  ("iso.3.6.1.4.1.20246.2.3.1.1.1.2.9.1.1.3.24", 10)  
}

THRESHOLD = 120


def send_mail(subject, body, to_email):
    try:
        from_email = "thephongca@gmail.com"
        password = "smynyresthaenvcn" 

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"[MAIL] Đã gửi cảnh báo tới {to_email}")
    except Exception as e:
        print("Lỗi gửi mail:", e)


def get_battery_time(ip):
    session = Session(hostname=ip, community="FPTHCM", version=2)

    for oid, scale in OIDS.values():
            result = session.get(oid)
            if result.value.isdigit():
                val = int(result.value)
                minutes = val * scale
                return minutes
    return 0


if __name__ == "__main__":
    for ip in list_ip:
        bt1 = get_battery_time(ip)
        if bt1 > 0:
            print(f"Thiết bị {ip} battery time: {bt1} phút")
            if bt1 < THRESHOLD:
                subject = f"[ALERT] Battery low at {ip}"
                body = f"Thiết bị {ip} chỉ còn {bt1} phút battery. Cần kiểm tra gấp!"
                send_mail(subject, body, "n21dcvt072@student.ptithcm.edu.vn")
        else:
            print(f"Thiết bị {ip} không lấy được dữ liệu")
