FROM python:3.6

WORKDIR /update_data
RUN apt-get update && apt-get install -y vim
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY __init__.py db.py downloader.py log.py parser.py run.py setting.py spider.py update_data.py update_grade.py temp_download.py ./

CMD ["python", "run.py"]
