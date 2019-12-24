import requests
import json
from pymongo import MongoClient

urls = ["https://raw.githubusercontent.com/bharatari/utd-grades/master/data/Fall%202017/fall2017.json",
        "https://raw.githubusercontent.com/bharatari/utd-grades/master/data/Fall%202018/fall2018.json",
        "https://raw.githubusercontent.com/bharatari/utd-grades/master/data/Spring%202018/spring2018.json",
        "https://raw.githubusercontent.com/bharatari/utd-grades/master/data/Spring%202019/spring2019.json",
        "https://raw.githubusercontent.com/bharatari/utd-grades/master/data/Summer%202018/summer2018.json"]

client = MongoClient("localhost", 27017)
db = client.Coursebook
col = db.utdgrades

for url in urls:
    resp = requests.get(url)
    selector = json.loads(resp.text)
    col.insert_many(selector)
