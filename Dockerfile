FROM python:3.10.10

COPY . .
WORKDIR /app

WORKDIR ..
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN rm -rf ./logs
RUN mkdir ./logs

EXPOSE 50007

ENTRYPOINT uvicorn main:app --host=0.0.0.0 --port=50007 --reload
