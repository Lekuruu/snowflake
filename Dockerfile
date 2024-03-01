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

ENV DOCKERIZE_VERSION v0.7.0
RUN ARCH=$(arch | sed s/aarch64/arm64/ | sed s/x86_64/amd64/) && wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-$ARCH-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-$ARCH-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-$ARCH-$DOCKERIZE_VERSION.tar.gz

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# This dockerfile requires you to have a volume that contains the source code for snowflake
# You can add this line, if you don't want to use a volume:
# COPY . .

ENTRYPOINT ["python", "./main.py"]