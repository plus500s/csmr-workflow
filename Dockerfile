FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements/base.txt /code/
RUN pip install -r base.txt
COPY . /code/
EXPOSE 8000
RUN python manage.py makemigrations workflow
RUN python manage.py migrate
RUN python manage.py loaddata fixture.json
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
