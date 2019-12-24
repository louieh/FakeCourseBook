FROM python:3.6

WORKDIR /Course-Search

COPY requirements.txt .

RUN apt-get update && apt-get install -y vim && pip install -r requirements.txt

COPY app app
COPY config.py course_search.py ./

EXPOSE 9000
CMD ["gunicorn", "-w", "4", "-b", ":9000", "--log-level", "debug", "course_search:app"]
