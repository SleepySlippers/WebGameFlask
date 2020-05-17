import smtplib
import socket


def send_mail(mail_address: str, text: str):
    mail_obj = smtplib.SMTP('smtp.gmail.com', 587)
    mail_obj.starttls()
    mail_obj.login('slippersecretorganization@gmail.com', 'easy4pass!')
    try:
        mail_obj.sendmail("slippersecretorganization@gmail.com",
                          mail_address, text)
    except socket.gaierror:
        return "Wrong email"
    mail_obj.quit()
