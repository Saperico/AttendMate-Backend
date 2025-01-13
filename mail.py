import smtplib
import random
import string

email = "sapijaszkoeryk@gmail.com"
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email, "oszj yufj puwv fyzp")

def send_email(receiver_email, password):
    subject = "AttendMate - Email Verification"
    message = "Welcome to AttendMate!\n \n \n \n Your password is: {} \n\n After you login you can change your password in your profile details".format(password)
    text = "Subject: {}\n\n{}".format(subject, message)
    server.sendmail(email, receiver_email, text)
    
def generate_password(length=12):
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    password = ''.join(random.choices(characters, k=length))
    return password