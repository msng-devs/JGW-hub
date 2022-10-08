FROM python:3.9.14

RUN pwd \
    ls

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENV TEST_DB_NAME docker_test
RUN python manage.py test

EXPOSE 50003
ENTRYPOINT python manage.py runserver
