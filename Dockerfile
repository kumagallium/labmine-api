FROM python:3.7
ENV PYTHONUNBUFFERED 1
COPY ./static /static/
WORKDIR /code
COPY requirements.txt /code/
RUN apt update && apt -y install netcat
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./src /code/

ENV DJANGO_SECRET_KEY=xxxx
ENV DJANGO_DB_NAME=dbname
ENV DJANGO_DB_USER=dbuser
ENV DJANGO_DB_HOST=dbhost
ENV DJANGO_DB_PASS=dbpass
ENV DJANGO_DB_PORT=3306

RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["sh","/code/entrypoint.sh"]