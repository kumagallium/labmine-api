FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./src /code/
COPY ./static /code/

ENV DJANGO_SECRET_KEY=xxxx
ENV DJANGO_DB_NAME=dbname
ENV DJANGO_DB_USER=dbuser
ENV DJANGO_DB_HOST=dbhost
ENV DJANGO_DB_PASS=dbpass
ENV DJANGO_DB_PORT=3306

ENV HOST 0.0.0.0
EXPOSE 8001
CMD ["sh","-c","python manage.py migrate && python manage.py runserver 0.0.0.0:8001"]