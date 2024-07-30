import smtplib, os, json
from email.message import EmailMessage
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def notify(message):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            message = json.loads(message)  #takes a file object and returns the json object
            mp3_fid = message.get("mp3_fid")
            sender_address = os.environ.get("GMAIL_USER")
            sender_pass = os.environ.get("GMAIL_PASS")
            recipient_address = message.get("username")

            # Creating message
            msg = EmailMessage()
            msg.set_content(
                f"Your MP3 file is ready for download.\nPlease visit: http://mp3converter.com/download?fid={mp3_fid} \nPlease note this link is valid only for 24 hours.")
            msg["Subject"] = "MP3 Conversion Complete"
            msg["From"] = sender_address
            msg["To"] = recipient_address

            session = smtplib.SMTP("smtp.gmail.com", 587)
            session.starttls()  #ensures security b/w our app and smtp server.
            session.login(sender_address, sender_pass)
            session.send_message(msg, sender_address, recipient_address)
            session.quit()
            print("Email sent successfully")
            return None  #success

        except Exception as e:
            logger.error(f"Error sending email (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
            
    return "error" #if failed