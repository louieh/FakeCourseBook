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
import requests
import logging
import os

client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = db.courses19spring

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config.from_object('config')

print(app.config['INSERT_DATA_TIME'])


def getRateId(name):
    rateuri = "http://search.mtvnservices.com/typeahead/suggest/?rows=20&q=" + name + "&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&siteName=rmp&group=on&group.field=content_type_s&group.limit=50"

    try:
        resp = requests.get(rateuri)
    except:
        return None, 'downloadfail'
    try:
        resp_parse = json.loads(resp.text)
        resp_parse_list = resp_parse.get('grouped').get('content_type_s').get('groups')[0].get('doclist').get('docs')
        for each_resp in resp_parse_list:
            if each_resp.get("schoolname_s") == 'University of Texas at Dallas':
                return each_resp.get('pk_id'), 'ok'
        return None, 'notfound'
    except:
        return None, 'parsefail'


def makesureDataSource():
    collection = db.courses19spring
    datasource = session.get('DATA_SOURCE')
    if datasource == '18f':
        collection = db.courses18fall
    elif datasource == '19s':
        collection = db.courses19spring
    return collection


@app.before_first_request
def before_first_request():
    session['DATA_SOURCE'] = '19s'  # 18f/19s


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/instructor/<name>')
def findrate(name):
    pk_id, reason = getRateId(name)
    if not pk_id:
        # logging.INFO(reason)
        return redirect('http://www.ratemyprofessors.com/search.jsp?query=%s' % name)

    return redirect('http://www.ratemyprofessors.com/ShowRatings.jsp?tid=%s' % pk_id)


@app.route('/changesource/<source>')
def changesource(source):
    session['DATA_SOURCE'] = source
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def search():
    collection = makesureDataSource()  # Reacquire collection

    item_list = ["class_title", "class_number", "class_section", "class_instructor", "class_day", "class_start_time",
                 "class_end_time", "class_location"]
    item_dict = session.get('item_dict')
    if not item_dict:
        item_dict = {}
    item_dict_result = {}

    if request.method == 'POST':
        for each_item in item_list:
            if request.form[each_item]:
                item_dict[each_item] = request.form[each_item]
        fuzzyquery = 1 if "fuzzyquery" in request.form else 0

        session['item_dict'] = item_dict
        session['fuzzyquery'] = fuzzyquery
        session['button'] = 'nowclass' if 'nowclass' in request.form else 'search'
        return redirect(url_for('search'))

    if item_dict and session.get('button') == 'search':
        if session.get('fuzzyquery'):
            for eachKey in item_dict.keys():
                item_dict_result[eachKey] = re.compile(str(item_dict.get(eachKey)), re.I)
        else:
            item_dict_result = item_dict
    elif session.get('button') == 'nowclass':
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

    session['item_dict'] = None
    session['fuzzyquery'] = None
    session['button'] = None
    return render_template('search.html', data=courses_list, Filter=item_dict,
                           DATA_SOURCE=session.get('DATA_SOURCE', '19s'))


if __name__ == '__main__':
    app.run()
