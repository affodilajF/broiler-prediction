# base images
FROM python:3.10.12-slim

RUN apt-get update && \
    apt-get install -y \
    curl \ 
    libpq-dev \
    gcc && \
    apt-get clean

RUN curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/10bfb27b-c589-4634-a372-5895f36ade2c/cert'

WORKDIR /broiler-model-api
COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . /broiler-model-api

EXPOSE 5000

CMD ["python3", "__init__.py"]