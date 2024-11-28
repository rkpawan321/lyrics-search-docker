FROM python:3.10.6-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "elastic_demo.wsgi:application"]

