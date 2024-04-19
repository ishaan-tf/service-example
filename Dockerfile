FROM python:3.9

WORKDIR /app

RUN pip install prometheus-client
COPY . .

CMD [ "python", "main.py" ]