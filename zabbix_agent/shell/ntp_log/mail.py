import base64
import smtplib
import sys
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

email_smtp_host = 'h1.icoremail.net'
email_user_name = 'zhangruiming@sotcbb.com'
email_passwd_base64 = b'WmhhbmcxMjM4JCE='
email_passwd = base64.b64decode(email_passwd_base64).decode()

msg_from = '全春祺<quanchunqi@sotcbb.com>'
msg_to = [sys.argv[1]]
msg_cc = sys.argv[2].split(',')
subject = sys.argv[3]
msg_content = sys.argv[4] + '\n'
msg_att_path = sys.argv[5]
msg_att_filename = msg_att_path.split('/')[-1]

msg = MIMEMultipart()

msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))
msg['From'] = Header(msg_from, 'utf-8')
msg['To'] = Header(', '.join(msg_to), 'utf-8')
msg['Cc'] = Header(', '.join(msg_cc), 'utf-8')

att = MIMEText(open(msg_att_path, 'rb').read(), 'base64', 'utf-8')
att["Content-Type"] = 'application/octet-stream'
att["Content-Disposition"] = 'attachment; filename=' + msg_att_filename
msg.attach(att)

msg['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(email_smtp_host, 25)
    smtpObj.login(email_user_name, email_passwd)
    smtpObj.sendmail(msg_from, msg_to + msg_cc, msg.as_string())
    # print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")
