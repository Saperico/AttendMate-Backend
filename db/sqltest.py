from sqlalchemy import create_engine, text

# Database connection details
USER = "appuser"
PASSWORD = "apppassword"
DATABASE_NAME = "AttendMate"
DATABASE_URI = "mysql+pymysql://{}:{}@localhost:3306/{}".format(USER, PASSWORD, DATABASE_NAME)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URI)

# Example query
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM attendanceStatus;"))
    print("Attendance Status Records:")
    for row in result:
        print(row)