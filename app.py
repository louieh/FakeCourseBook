from flask import Flask, request, redirect, url_for, session, escape, jsonify, abort
from flask import render_template
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_bootstrap import Bootstrap
from flask import g

from pymongo import MongoClient
import re
import datetime
import json
import requests
import logging
import os
import redis

client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = db.CourseForSearch
TIMEDELTA = 5  # summer time

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
moment = Moment(app)


def getDataupdatetime():
    try:
        redis_url = redis.StrictRedis.from_url('localhost')
        data_update_time = redis_url.get('data_update_time')
    except:
        return None
    return data_update_time


def getRateId(name):
    rateuri = "https://search-production.ratemyprofessors.com/solr/rmp/select/?rows=20&wt=json&q=" + name + "&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&group.limit=50"
    try:
        resp = requests.get(rateuri)
    except:
        return None, 'downloadfail'
    try:
        resp_parse = json.loads(resp.text)
        resp_parse_list = resp_parse.get('response').get('docs')
        for each_resp in resp_parse_list:
            if each_resp.get("schoolname_s") == 'University of Texas at Dallas':
                return each_resp.get('pk_id'), 'ok'
        return None, 'notfound'
    except:
        return None, 'parsefail'


@app.before_first_request
def before_first_request():
    session['DATA_SOURCE'] = '19F'  # 19F/19S


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/findrate/<name>')
def findrate(name):
    pk_id, reason = getRateId(name)
    if not pk_id:
        # logging.INFO(reason)
        return redirect('http://www.ratemyprofessors.com/search.jsp?query=%s' % name)

    return redirect('http://www.ratemyprofessors.com/ShowRatings.jsp?tid=%s' % pk_id)


@app.route('/changesource/<source>')
def changesource(source):
    session['DATA_SOURCE'] = source
    data = list(collection.find({"class_term": source}, {"_id": 0}))
    return jsonify(data)


@app.route('/', methods=['GET', 'POST'])
def search():
    term = session.get("DATA_SOURCE", "19F")  # get term first

    item_list = ["class_title", "class_number", "class_section", "class_instructor",
                 "class_day", "class_start_time",
                 "class_end_time", "class_location"]  # "class_term", "class_status" 非前端筛选条件
    item_dict = session.get('item_dict')
    if not item_dict:
        item_dict = {}
    item_dict_result = {}
    item_dict_result["class_term"] = term

    if request.method == 'POST':
        for each_item in item_list:
            if each_item in request.form and request.form[each_item]:
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
        time_now_all = (datetime.datetime.utcnow() - datetime.timedelta(hours=TIMEDELTA)).strftime('%A-%H:%M')
        week_now, time_now = time_now_all.split('-')
        item_dict_result['class_day'] = re.compile(week_now, re.I)
        item_dict_result['class_start_time'] = {"$lte": time_now}
        item_dict_result['class_end_time'] = {"$gte": time_now}

    courses_list = list(collection.find(item_dict_result, {"_id": 0}))
    count = len(courses_list)

    session['item_dict'] = None
    session['fuzzyquery'] = None
    session['button'] = None
    data_update_time = getDataupdatetime()
    if data_update_time:
        data_update_time = str(data_update_time, encoding='utf-8')
    return render_template('search.html', data=courses_list, Filter=item_dict,
                           data_update_time=data_update_time)


@app.route('/graph/professor/')
@app.route('/graph/professor/<professor>')
@app.route('/graph/course')
@app.route('/graph/course/<coursesection>')
def graph_pro(professor=None, coursesection=None):
    terms = ['19F', '19S', '18F', '18U', '18S', '17F', '17U', '17S', '16F', '16U', '16S', '15F', '15U', '15S',
             '14F', '14U', '14S', '13F', '13U', '13S', '12F', '12U', '12S', '11F', '11U', '11S', '10F',
             '10U', '10S']

    if not professor and not coursesection:
        if "graph/professor" in request.url:
            professor_set = set()
            professor_dict_list = list(db.CourseForGraph.find({}, {"class_instructor": 1, "_id": 0}))
            for eachdict in professor_dict_list:
                for each in eachdict.get("class_instructor"):
                    if "Staff" not in each:
                        professor_set.add(each)
            professor_char_dict = {}
            for i in range(65, 91):  # 创建key为字母的字典，键值为空列表
                professor_char_dict[chr(i)] = []
            for each_professor_name in professor_set:  # insert professor name to professor_char_dict based on the first letter of their name
                professor_char_dict[each_professor_name[0]].append(each_professor_name)
            professor_list_list = []
            for eachkey in professor_char_dict.keys():  # insert the key_value of professor_char_dict to a new list
                if professor_char_dict.get(eachkey):
                    professor_list_list.append(professor_char_dict.get(eachkey))
            return render_template("graph.html", professor_list_list=professor_list_list)
        elif "graph/course" in request.url:
            cou_set = set()
            cou_dict_list = list(db.CourseForGraph.find({}, {"class_title": 1, "class_section": 1, "_id": 0}))
            for eachcou_dict in cou_dict_list:
                eachcou_dict["class_section"] = eachcou_dict.get("class_section").split(".")[0]
                cou_set.add(json.dumps(eachcou_dict))
            cou_dict_list_temp = sorted(list(cou_set))
            cou_dict_list_fin = []
            for eachcou_dict in cou_dict_list_temp:
                cou_dict_list_fin.append(json.loads(eachcou_dict))
            return render_template("graph.html", cou_dict_list=cou_dict_list_fin)

    if professor:
        if not list(db.CourseForGraph.find({"class_instructor": professor})):
            abort(404)

        term_dict_list = []
        for eachterm in terms:
            term_dict = {}
            course_dict_list = []
            all_course_list = list(
                db.CourseForGraph.find({"class_term": eachterm, "class_instructor": professor}, {"_id": 0}))
            if all_course_list:
                for eachcourse in all_course_list:
                    course_dict = {}
                    course_dict["name"] = eachcourse.get("class_title")
                    course_dict["value"] = eachcourse.get("class_section").split(" ")[-1].split(".")[0]
                    course_dict_list.append(course_dict)
            term_dict["name"] = eachterm
            term_dict["children"] = course_dict_list
            term_dict_list.append(term_dict)
        professor_json = {"name": professor, "children": term_dict_list}
        return render_template('graph.html', professor_name=professor,
                               professor_json=professor_json)
    if coursesection:
        all_course_list = list(db.CourseForGraph.find({"class_section": {"$regex": coursesection}}, {"_id": 0}))
        if not all_course_list:
            abort(404)
        else:
            course_name = all_course_list[0].get("class_title")

        term_dict = {}
        for eachterm in terms:
            term_dict[eachterm] = []

        for eachcourse_dict in all_course_list:
            professorname_list = eachcourse_dict.get("class_instructor")
            term = eachcourse_dict.get("class_term")
            for eachprofessorname in professorname_list:
                temp_professorname_dict = {"name": eachprofessorname, "value": eachprofessorname}
                if not temp_professorname_dict in term_dict[term]:
                    term_dict[term].append(temp_professorname_dict)

        final_list = []
        for eachterm in terms:
            temp_final_dict = {"name": eachterm, "children": term_dict.get(eachterm)}
            final_list.append(temp_final_dict)
        final_dict = {"name": coursesection, "children": final_list}
        return render_template('graph.html', course_section=coursesection.lower().replace(' ', ''),
                               course_name=course_name,
                               course_json=final_dict)


@app.route('/jobinfo')
def jobinfo():
    job_filter, num = get_jobinfo_args()
    if db.JobInfo.find(job_filter).count() - num <= 10:
        return render_template('jobinfo.html')
    else:
        data = db.JobInfo.find(job_filter, {'_id': 0, 'name': 1, 'company': 1, 'city': 1, 'create_time': 1}).sort(
            [{'create_time', -1}]).skip(num).limit(10)

        return render_template('jobinfo.html', data=list(data), job_filter=job_filter)


def get_jobinfo_args():
    job_filter = {}

    city_index = request.args.get('city')
    city = city_dict.get(city_index)
    if city:
        job_filter['city'] = city

    firm_index = request.args.get('firm')
    firm = firm_dict.get(firm_index)
    if firm:
        job_filter['company'] = firm

    num = request.args.get('num')
    if not num:
        num = 0
    else:
        num = int(num)
    return job_filter, num


@app.route('/jobinfodata')
def jobinfodata():
    job_filter, num = get_jobinfo_args()

    data = db.JobInfo.find(job_filter, {'_id': 0, 'name': 1, 'company': 1, 'city': 1, 'create_time': 1}).sort(
        [{'create_time', -1}]).skip(num).limit(10)
    ifnext = not db.JobInfo.find(job_filter).count() - num <= 10
    ifpre = num > 0
    result = {'data': list(data), 'ifnext': ifnext, 'ifpre': ifpre}
    return jsonify(result)


city_dict = {
    '1': '北京',
    '2': '上海',
    '3': '杭州',
    '4': '深圳',
    '5': '武汉',
}

firm_dict = {
    '1': 'bytedance',
    '2': 'baidu',
    '3': 'bilibili',
}


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
