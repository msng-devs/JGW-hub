FROM python:3.10.10

COPY . .
WORKDIR /JGW_hub
RUN echo "is_debug = 0" > debug.py

WORKDIR ..
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN rm -rf ./logs
RUN mkdir ./logs

EXPOSE 50007

ENTRYPOINT gunicorn --bind=0.0.0.0:50007 JGW_hub.wsgi:application
