FROM python:3.7-slim

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY ./app.py ./evaluate_score.py ./wsgi.py ./gunicorn.sh ./

RUN chmod +x /app/gunicorn.sh
CMD /app/gunicorn.sh
