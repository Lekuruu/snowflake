FROM python:3.12.1-alpine3.18
ARG TARGETARCH

RUN apk add \
    openssl \
    build-base \
    openssl-dev \
    libffi-dev \
    redis \
    postgresql-client

WORKDIR /usr/src/snowflake

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "./main.py"]