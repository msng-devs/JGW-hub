FROM python:3.9.14

RUN pwd \
    ls

RUN \
  echo "install packages" \
  python -m pip install --upgrade pip \
  pip install -r requirements.txt

ENV TEST_DB_NAME docker_test
RUN \
  echo "django test start" \
  python manage.py test \

EXPOSE 50003
