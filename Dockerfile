FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/app

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0:8001"]