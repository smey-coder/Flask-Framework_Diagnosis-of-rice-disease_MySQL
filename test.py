from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config.from_object("config.Config")
mail = Mail(app)

with app.app_context():
    msg = Message("Test Email", recipients=["sannokea@gmail.com"])
    msg.body = "Hello! This is a test email from Flask."
    mail.send(msg)
    print("Email sent!")
