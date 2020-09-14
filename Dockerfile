FROM python:3.6-slim

COPY . /root

WORKDIR /root

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT python main.py
EXPOSE 5000