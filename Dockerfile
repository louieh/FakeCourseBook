FROM python:3.6

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:djcj/hybrid && apt-get install -y ffmpeg

WORKDIR /Course-Search

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY instance instance
COPY static static
COPY templates templates
COPY util util
COPY app.py log.py update_data ./

EXPOSE 9000
CMD ["gunicorn", "-w", "4", "-b", ":9000", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
