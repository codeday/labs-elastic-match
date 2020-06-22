FROM python:3.7-slim

RUN mkdir /app
WORKDIR /app

COPY api/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY api/app.py api/evaluate_score.py api/wsgi.py api/gunicorn.sh ./

RUN chmod +x /app/gunicorn.sh
CMD /app/gunicorn.sh
