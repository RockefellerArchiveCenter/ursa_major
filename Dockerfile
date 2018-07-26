FROM python:3.5
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 ADD . /code/
 ADD requirements.txt /code/
 RUN pip install --upgrade pip && pip install -r requirements.txt
