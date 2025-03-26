FROM python:3.13-alpine AS dev

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/app/main.py" ]

COPY ./generated /app/generated

COPY ./main.py /app/main.py
