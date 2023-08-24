import smtplib


def send_mail(mail, link, name):
    if mail is None or mail == '':
        return

    server = smtplib.SMTP('smtp.email.com', 465)
    server.starttls()

    server.login('no_reply_vietucfamily@email.com', 'VietUc@2023')
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Đăng ký tham gia Việt Úc Party 2023"
    msg['From'] = 'no_reply_vietucfamily@outlook.com'
    msg['To'] = mail

    # Create the body of the message (a plain-text and an HTML version).
    text = f"Chào {name}\nXin cảm ơn anh chị đã đăng ký tham Việt Úc Party 2023\nĐây là mã QR của anh chị, khi tham gia sự kiện anh chị hãy dùng mã này để check in vào cửa"
    html = f"""\
    <html>
      <head></head>
      <body>
        <p>Chào {name}<br>
           Xin cảm ơn anh chị đã đăng ký tham Việt Úc Party 2023<br>
           <b><a href="{link}">Đây</a> là mã QR của anh chị, khi tham gia sự kiện anh chị hãy dùng mã này để check in vào cửa</b>
        </p>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    server.sendmail('no_reply_vietucfamily@email.com', mail, msg.as_string())
    server.quit()
