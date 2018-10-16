from flask import Flask, request, redirect
from flask import render_template
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_bootstrap import Bootstrap

from pymongo import MongoClient
import re
import time
import datetime

client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = db.courses

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    item_list = ["class_title", "class_number", "class_section", "class_instructor", "class_day", "class_start_time",
                 "class_end_time", "class_location"]
    item_dict = {}
    if request.method == 'POST':
        for each_item in item_list:
            if request.form[each_item]:
                item_dict[each_item] = request.form[each_item]
        fuzzyquery = 1 if "fuzzyquery" in request.form else 0
        if 'search' in request.form:
            if "class_section" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_section'] = re.compile(str(item_dict.get("class_section")), re.I)
            if "class_number" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_number'] = re.compile(str(item_dict.get("class_number")), re.I)
            if "class_title" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_title'] = re.compile(str(item_dict.get("class_title")), re.I)
            if "class_instructor" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_instructor'] = re.compile(str(item_dict.get("class_instructor")), re.I)
            if "class_day" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_day'] = re.compile(str(item_dict.get("class_day")), re.I)
            if "class_location" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_location'] = re.compile(str(item_dict.get("class_location")), re.I)

            courses_list = list(collection.find(item_dict))
            count = len(courses_list)
            return render_template('search.html', data=courses_list, count=count)
        if 'nowclass' in request.form:
            if "class_location" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_location'] = re.compile(str(item_dict.get("class_location")), re.I)
            if "class_instructor" in item_dict.keys():
                if fuzzyquery:
                    item_dict['class_instructor'] = re.compile(str(item_dict.get("class_instructor")), re.I)
            week_now = time.strftime("%A", time.localtime(time.time()))
            time_now = (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime('%H:%M')
            item_dict['class_day'] = re.compile(week_now, re.I)
            item_dict['class_start_time'] = {"$lte": time_now}
            item_dict['class_end_time'] = {"$gte": time_now}
            courses_list = list(collection.find(item_dict))
            count = len(courses_list)
            return render_template('search.html', data=courses_list, count=count)
    return render_template('search.html')


if __name__ == '__main__':
    app.run()
