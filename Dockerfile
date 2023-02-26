FROM python:3.9.14

COPY . .
WORKDIR /JGW_hub
RUN echo "is_debug = 0" > debug.py

WORKDIR ..
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENV TEST_DB_NAME docker_test
ENV TEST_DB_NAME_API docker_test_api
RUN python manage.py test

EXPOSE 50003

ENTRYPOINT gunicorn --bind=0.0.0.0:50003 JGW_hub.wsgi:application
