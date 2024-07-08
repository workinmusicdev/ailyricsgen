import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(subject, message, recipient_email):
    sender_email = "guedjegedeon03@gmail.com"
    sender_password = "odtoljgqbzjdhcnh"  # Assurez-vous que c'est un mot de passe d'application
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            if recipient_email:
                server.sendmail(sender_email, recipient_email, msg.as_string())
            #
            server.sendmail(sender_email, "workinmusic.app@gmail.com", msg.as_string())

            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
