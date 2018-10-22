from flask import Flask, request, redirect, url_for, session, escape
from flask import render_template
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_bootstrap import Bootstrap

from pymongo import MongoClient
import re
import datetime
import json

client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = db.courses

app = Flask(__name__)
app.secret_key = 'sjoifejsoiejfo'


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def search():
    item_list = ["class_title", "class_number", "class_section", "class_instructor", "class_day", "class_start_time",
                 "class_end_time", "class_location"]
    item_dict = session.get('item_dict')
    if not item_dict:
        item_dict = {}
    item_dict_result = {}
    if item_dict and session.get('button') == 'search':
        if session.get('fuzzyquery'):
            for eachKey in item_dict.keys():
                item_dict_result[eachKey] = re.compile(str(item_dict.get(eachKey)), re.I)
        else:
            item_dict_result = item_dict
    elif item_dict and session.get('button') == 'nowclass':
        if "class_location" in item_dict.keys():
            if session.get('fuzzyquery'):
                item_dict_result['class_location'] = re.compile(str(item_dict.get("class_location")), re.I)
            else:
                item_dict_result['class_location'] = item_dict.get('class_location')
        if "class_instructor" in item_dict.keys():
            if session.get('fuzzyquery'):
                item_dict_result['class_instructor'] = re.compile(str(item_dict.get("class_instructor")), re.I)
            else:
                item_dict_result['class_instructor'] = item_dict.get('class_instructor')
        time_now_all = (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime('%A-%H:%M')
        week_now, time_now = time_now_all.split('-')
        item_dict_result['class_day'] = re.compile(week_now, re.I)
        item_dict_result['class_start_time'] = {"$lte": time_now}
        item_dict_result['class_end_time'] = {"$gte": time_now}

    courses_list = list(collection.find(item_dict_result))
    count = len(courses_list)

    if request.method == 'POST':
        for each_item in item_list:
            if request.form[each_item]:
                item_dict[each_item] = request.form[each_item]
        fuzzyquery = 1 if "fuzzyquery" in request.form else 0

        session['item_dict'] = item_dict
        session['fuzzyquery'] = fuzzyquery
        session['button'] = 'nowclass' if 'nowclass' in request.form else 'search'
        return redirect(url_for('search'))
    session['item_dict'] = ''
    session['fuzzyquery'] = ''
    session['button'] = ''
    return render_template('search.html', data=courses_list, count=count)


if __name__ == '__main__':
    app.run()
