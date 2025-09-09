from datetime import datetime
from pprint import pprint
from RAD_LIB.Telnet import TELNET
from RAD_LIB.Snmp import SNMP
from RAD_LIB.MongoDB import MongoDB
import re, time, subprocess
from xml.etree import ElementTree
import requests, yaml, traceback, random, os
from queue import PriorityQueue, Queue
from threading import Thread, Lock
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

list_ip = [
    "11.57.143.22",
    "11.57.143.23",
    "11.54.149.11",
    "11.61.144.71",
    "11.61.144.72",
]

OIDS = {
    "Enatel": ("iso.3.6.1.4.1.21940.2.4.2.24.0", 1),     
    "Delta":  ("iso.3.6.1.4.1.20246.2.3.1.1.1.2.9.1.1.3.24", 10)  
}

THRESHOLD = 120

def send_command_server(command:str):
    respone =  subprocess.Popen(command,  shell=True, stdout=subprocess.PIPE).stdout
    outputping =  respone.read().decode()
    return outputping

def send_mail(subject, body, to_email):
    try:
        from_email = "thephongca@gmail.com"
        password = "erajeljnkbpphvsp" 

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
        print("Gửi mail thành công!")
    except Exception as e:
        print("Lỗi gửi mail:", e)

def get_battery_time(ip):
    for oid, scale in OIDS.values():
        cmd = ["snmpget", "-v2c", "-c", "FPTHCM", ip, oid]
        result = subprocess.run(cmd, capture_output=True, text=True)

        res = re.findall(r"INTEGER:\s+(\d+)", result)
        if res:  
            val = int(res[0])
            minutes =val * scale   
            return minutes
    return 0

for ip in list_ip:
    battery_time = get_battery_time(ip)
    if battery_time is not None:
        if battery_time < THRESHOLD:
            subject = f"Battery warning at {ip}"
            body = f"Thiết bị {ip} chỉ còn {battery_time} phút battery. Cần kiểm tra gấp!"
            send_mail(subject, body, "n21dcvt072@student.ptithcm.edu.vn")
    else:
        print(f"Thiết bị {ip} không lấy được dữ liệu")