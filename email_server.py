import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


SENDER_EMAIL    =  # ← your alternate gmail
RECEIVER_EMAIL  =       # User email



def send_credentials(user_email, password, name):
    """
    Send extracted credentials email

    Input  → user_email : email extracted from resume
             password   : auto generated password
             name       : candidate first name
    Output → Email delivered to RECEIVER_EMAIL
    """
    try:
        
        sender_password = os.getenv("EMAIL_PASSWORD")

        
        msg = MIMEMultipart()
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = RECEIVER_EMAIL
        msg["Subject"] = f"New Profile Created — {name}"

        
        body = f"""
Hello,

A new candidate profile has been successfully created.

Candidate Details:
──────────────────────────────
Candidate Name : {name}
Email ID       : {user_email}
Password       : {password}
──────────────────────────────

Login URL : http://localhost:8501

Regards,
AI Profile Onboarder System
        """

        msg.attach(MIMEText(body, "plain"))

       
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, sender_password)
            server.sendmail(
                SENDER_EMAIL,
                RECEIVER_EMAIL,
                msg.as_string()
            )

        print(f" Email sent to {RECEIVER_EMAIL}")
        return True

    except Exception as e:
        raise RuntimeError(f"Email sending failed: {e}")