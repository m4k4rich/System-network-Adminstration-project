FROM python:3.10.8

WORKDIR /app

EXPOSE 8000

COPY ./requirements.txt  /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./templates /app/templates
COPY main.py /app/ 

CMD [ "uvicorn", "main:app", "--host=0.0.0.0", "--port=8000" ]
