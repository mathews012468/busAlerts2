#for some reason uwsgi and lxml refuse to build for 3.11
FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP api.py

RUN [ "python", "prepare_config.py"]

CMD [ "uwsgi", "--ini", "config.ini"]