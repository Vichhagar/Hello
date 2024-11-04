FROM ubuntu:latest

# Update the package manager's cache
RUN apt-get update && apt-get install -y build-essential

# Install Python 3.9 and pip
RUN apt-get -y install python3
RUN apt-get install -y python3.9 python3-pip

# Install the MySQL development libraries
RUN apt-get -y install libmysqlclient-dev

# Install the missing system package
RUN apt-get -y install libio-socket-ssl-perl

# Install other dependencies
# RUN pip install twisted-iocpsupport

# Set the working directory
WORKDIR /usr/app

# Copy the requirements file and install the dependencies
COPY requirements.txt /usr/app/requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the project files
COPY . /usr/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the database environment variables
ENV DB_NAME='hello'
ENV DB_USER='root'
ENV DB_PASSWORD=''
ENV DB_HOST=db

# Run the command on container startup
# CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
CMD python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000
