from flask_mail import Message
from flask import render_template
from threading import Thread
from flask import current_app

from app import mail

# 异步电子邮件
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# 发送电子邮件的帮助函数    
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
