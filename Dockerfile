FROM python:3.11-slim AS dev

WORKDIR /app

COPY ./requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Install proto tools and generate proto files
COPY ./server.proto /app/
RUN pip install grpcio-tools && \
    python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. server.proto

CMD [ "python", "/app/main.py" ]

EXPOSE 9990

COPY ./server_pb2_grpc.py /app/server_pb2_grpc.py
COPY ./server_pb2.py /app/server_pb2.py
COPY ./server_pb2.pyi /app/server_pb2.pyi
COPY ./config.py /app/config.py
COPY ./db /app/db
COPY ./game /app/game
COPY ./main.py /app/main.py
