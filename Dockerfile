FROM python:3.6-alpine as base

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local

RUN mkdir /app
RUN mkdir /app/src

COPY start.py /app
COPY src /app/src

WORKDIR /app
ENTRYPOINT ["python", "start.py"]