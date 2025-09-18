from easysnmp import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

DEVICES = {
    "11.57.143.22": "HCMP01001PWDE1U",
    "11.57.143.23": "HCMP01002PWDE1U",
    "11.54.149.11": "HCMP47602PWDE1U",
    "11.61.144.71": "BDGP11501PWDE1U",
    "11.61.144.72": "BDGP11502PWDE1U"
}

OIDS = {
    "Enatel": ("iso.3.6.1.4.1.21940.2.4.2.24.0", 1),
    "Delta":  ("iso.3.6.1.4.1.20246.2.3.1.1.1.2.9.1.1.3.24", 10)
}

THRESHOLD = 120

def name_power(name: str):
    pop = name[:3]
    return f"Nguồn INF-{pop}-{name}"


def html_mail(source_name, ip, battery_time):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif;">

        <h3 style="color:red;">
          🆘 CRITICAL - {source_name} - {ip} thời gian backup pin còn {battery_time} phút !!!
        </h3>

        <table cellpadding="5" style="font-size:14px;">
          <tr><td>🟨 Địa chỉ IP:</td><td>{ip}</td></tr>
          <tr><td>🟨 Tên nguồn:</td><td>{source_name}</td></tr>
          <tr><td>🟨 Thời gian pin còn:</td><td>{battery_time} phút</td></tr>
          <tr><td>🟨 Thời gian cảnh báo:</td><td>{now}</td></tr>
        </table>

      </body>
    </html>
    """


def send_mail_html(server, from_email, to_email, subject, html_body):
    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        server.sendmail(from_email, to_email, msg.as_string())
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
    from_email = "thephongca@gmail.com"
    password = "smynyresthaenvcn"
    to_email = "n21dcvt072@student.ptithcm.edu.vn"
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)

        for ip, source_name in DEVICES.items():
            bt1 = get_battery_time(ip)
            if bt1 > 0 and bt1 < THRESHOLD:
                print(f"Thiết bị {ip} battery time: {bt1} phút")
                full_name = name_power(source_name)
                subject = f"⛔️⛔️⛔ {full_name} - {ip} cảnh báo thời gian backup pin còn {bt1} phút"
                body = html_mail(full_name, ip, bt1)
                send_mail_html(server, from_email, to_email, subject, body)

        server.quit()

    except Exception as e:
        print("Lỗi khi kết nối Gmail:", e)
