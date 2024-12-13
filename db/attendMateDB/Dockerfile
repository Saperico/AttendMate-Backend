# Use the official MySQL image
FROM mysql:latest

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=AttendMate
ENV MYSQL_USER=appuser
ENV MYSQL_PASSWORD=apppassword

# Copy the schema into the Docker container
COPY schema.sql /docker-entrypoint-initdb.d/

# Expose the MySQL default port
EXPOSE 3306