FROM python:3

WORKDIR /app

RUN pip install sqlalchemy grpcio

ADD ./src/ /app/

ENTRYPOINT ["python3", "/app/main.py", "--database $DATABASE", "--tcp-server $TCP-SERVER" "--http-server $HTTP-SERVER"]
