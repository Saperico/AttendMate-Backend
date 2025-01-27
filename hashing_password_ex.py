
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

password = bcrypt.generate_password_hash("student").decode('utf-8')
print(password)