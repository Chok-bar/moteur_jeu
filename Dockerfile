FROM python:3.13-alpine AS dev

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/app/main.py" ]

EXPOSE 9990

COPY ./server_pb2_grpc.py /app/server_pb2_grpc.py
COPY ./server_pb2.py /app/server_pb2.py
COPY ./server_pb2.pyi /app/server_pb2.pyi

COPY ./main.py /app/main.py
