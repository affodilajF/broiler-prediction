# base images
FROM python:3.10.12-slim

# Install PostgreSQL development libraries
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean

# workdir is used to set the pwd inside docker container
WORKDIR /broiler-model-api
COPY requirements.txt /requirements.txt

# Install pip dependancy.
RUN pip install -r /requirements.txt

# copy whole directory inside /code working directory.
COPY . /broiler-model-api

# This command execute at the time when container start.
CMD ["python3", "__init__.py"]