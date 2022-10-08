FROM python:3.9.14

COPY . .
RUN ls

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENV TEST_DB_NAME docker_test
RUN python manage.py test

EXPOSE 8000

ENTRYPOINT gunicorn --bind=0.0.0.0:8000 JGW_hub.wsgi:application
