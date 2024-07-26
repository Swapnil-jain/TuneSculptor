import smtplib, os, json
from email.message import EmailMessage

def notify(message):
    try:
        message = json.loads(message)  #takes a file object and returns the json object
        mp3_fid = message.get("mp3_fid")
        sender_address = os.environ.get("GMAIL_USER")
        sender_pass = os.environ.get("GMAIL_PASS")
        recipient_address = message.get("username")

        # Creating message
        msg = EmailMessage()
        msg.set_content(
            f"Your MP3 file is ready for download.\nVisit http://mp3converter.com/download?fid={mp3_fid}")
        msg["Subject"] = "MP3 Conversion Complete"
        msg["From"] = sender_address
        msg["To"] = recipient_address

        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()  #ensures security b/w our app and smtp server.
        session.login(sender_address, sender_pass)
        session.send_message(msg, sender_address, recipient_address)
        session.quit()
        print("Email sent successfully")

    except Exception as e:
        print(e)
        return e