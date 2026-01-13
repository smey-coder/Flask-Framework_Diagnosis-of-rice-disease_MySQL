from flask import Flask
from config import Config
from extensions import mail
from flask_mail import Message

app = Flask(__name__)
app.config.from_object(Config)
mail.init_app(app)

with app.app_context():
    msg = Message(
        subject="Test Email",
        recipients=[Config.MAIL_USERNAME],
        body="✅ Flask-Mail is working with Gmail App Password!"
    )
    try:
        mail.send(msg)
        print("✅ Test email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)
