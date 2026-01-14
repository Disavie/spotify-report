import smtplib
from email.message import EmailMessage
import ssl # For a secure connection
MY_EMAIL = "davisstermer@gmail.com"
APP_PASS = "aqqc vlcq xwyk tzxv "

# --- Email Credentials and Content ---
def send_email(receiver,subject, body):

    sender_email = MY_EMAIL
    app_password = APP_PASS # Use the app password, not your normal password
    receiver_email = receiver

    # Create the email message object
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # --- Send the Email via Gmail's SMTP Server ---
    smtp_server = "smtp.gmail.com"
    smtp_port = 587 # Port for TLS encryption

    try:
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Connect to the server and start TLS encryption
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # Optional, but good practice
            server.starttls(context=context)
            server.login(sender_email, app_password)
            server.send_message(msg)
            print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")