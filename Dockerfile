FROM python:3.6

WORKDIR /Course-Search

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY instance instance
COPY static static
COPY templates templates
COPY util util
COPY app.py log.py update_data.py ./

EXPOSE 9000
CMD ["gunicorn", "-w", "4", "-b", ":9000", "--log-level", "debug", "app:app"]