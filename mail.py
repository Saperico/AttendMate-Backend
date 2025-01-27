import smtplib
import random
import string

email = "pwr.attendmate@gmail.com"
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email, "uuua nqjl sctx ykoc")

def send_email(receiver_email, password):
    subject = "AttendMate - Email Verification"
    login_url = "http://localhost:3000/login"
    message = f"""
    Welcome to AttendMate!

    Your password is: {password}

    After you login, you can change your password in your profile details.

    You can log in <a href="{login_url}">here</a>.
    """
    
    # HTML formatted message
    html_message = f"""
    <html>
        <body>
            <p>Welcome to AttendMate!</p>
            <p>Your password is: <strong>{password}</strong></p>
            <p>After you login, you can change your password in your profile details.</p>
            <p>You can log in <a href="{login_url}">here</a>.</p>
        </body>
    </html>
    """
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = receiver_email

    msg.attach(MIMEText(html_message, 'html'))
    server.sendmail(email, receiver_email, msg.as_string())

def generate_password(length=12):
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    password = ''.join(random.choices(characters, k=length))
    return 
