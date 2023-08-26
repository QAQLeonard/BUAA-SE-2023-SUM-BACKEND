import smtplib


def send_email(email, code):
    from email.mime.text import MIMEText
    from email.header import Header

    # 配置SMTP服务器和端口
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    smtp_user = 'ticketdistance@gmail.com'
    smtp_pass = 'ltnrwkespkxkqtok'

    # 创建SMTP对象
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_user, smtp_pass)

    # 创建邮件内容
    validity_duration = 10  # 假设验证码有效时间是 10 分钟

    msg = MIMEText(f'Your verification code is {code}. This code will expire in {validity_duration} minutes.', 'plain',
                   'utf-8')
    msg['From'] = Header(smtp_user)
    msg['To'] = Header(email)
    msg['Subject'] = Header('Verification code')

    # 发送邮件
    server.sendmail(smtp_user, [email], msg.as_string())
    server.quit()
