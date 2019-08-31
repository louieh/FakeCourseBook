FROM python:3.6

WORKDIR /Course-Search
RUN apt-get update && apt-get install -y vim
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY util util
COPY update_data update_data
COPY .env config.py course_search.py ./

EXPOSE 9000
CMD ["gunicorn", "-w", "4", "-b", ":9000", "--log-level", "debug", "course_search:app"]
