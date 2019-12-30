from flask import render_template, session, redirect, url_for, jsonify, request, abort
from flask import current_app
from . import main
from pymongo import MongoClient
import re
import datetime
import json
import requests
import redis
from lxml import html
from collections import defaultdict


def getDataupdatetime():
    try:
        redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        data_update_time = redis_client.get(REDIS_UPDATE_TIME_KEY)
        data_update_next_time = redis_client.get(REDIS_UPDATE_NEXT_TIME_KEY)
    except:
        return None
    return data_update_time, data_update_next_time


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
            if 'University of Texas at Dallas' in each_resp.get("schoolname_s"):
                return each_resp.get('pk_id'), 'ok'
        return None, 'notfound'
    except:
        return None, 'parsefail'


@main.route('/get_put_search_tool_status/<status>')
@main.route('/get_put_search_tool_status')
def get_put_search_tool_status(status=None):
    if status is not None:
        if status == "false":
            session['search_tool'] = False
        else:
            session['search_tool'] = True
        return jsonify("ok")
    else:
        return jsonify({"status": session['search_tool']})


@main.route('/custom_search_fun/<professor_name>')
def custom_search_fun(professor_name):
    # https://personal.utdallas.edu/~jcobb/
    # https://cs.utdallas.edu/people/faculty/cobb-jorge/
    # https://profiles.utdallas.edu/cobb
    # https://utdallas.edu/~kyle.fox/
    # https://www.utdallas.edu/~bhavani.thuraisingham/
    prof_link_url = list(db.profIntroLinks.find({"prof": professor_name}, {"_id": 0}))
    if prof_link_url:
        links = prof_link_url[0].get("links")
        if links.get("personal"):
            return jsonify({"link": links.get("personal")})
        elif links.get("faculty"):
            return jsonify({"link": links.get("faculty")})
        else:
            return jsonify({"link": links.get("profiles")})
    url = "https://www.googleapis.com/customsearch/v1?cx={0}&q={1}&key={2}".format(
        current_app.config.get('CUSTOM_SEARCH_UTD_ID'), professor_name, current_app.config.get('CUSTOM_SEARCH_KEY'))
    try:
        resp = requests.get(url)
    except Exception as e:
        return jsonify({"error": str(e)})
    links_dict = {"links": {}, "prof": professor_name}
    resp_json = json.loads(resp.text)
    resp_items = resp_json.get("items")
    res_link = None

    def name_in_something(something, name_list=professor_name.split(" ")):
        for name in name_list:
            if name.lower() in something:
                return True
        return False

    if resp_items:
        for resp_item in resp_items:
            link = resp_item.get("link")
            title = resp_item.get("title")
            if not "personal" in links_dict["links"] and \
                    (re.search("^https://personal.utdallas.edu/~", link) or
                     re.search("^https://utdallas.edu/~", link) or
                     re.search("^https://www.utdallas.edu/~", link)) and \
                    (name_in_something(link.split("~")[-1]) or name_in_something(title)):
                links_dict["links"]["personal"] = link
                if not res_link:
                    res_link = link
            if not "faculty" in links_dict["links"] and re.search("/people/faculty/", link) and name_in_something(link):
                links_dict["links"]["faculty"] = link
                if not res_link:
                    res_link = link
            if not "profiles" in links_dict["links"] and re.search("^https://profiles.utdallas.edu/",
                                                                   link) and name_in_something(link):
                links_dict["links"]["profiles"] = link
                if not res_link:
                    res_link = link
        if links_dict.get("links"):
            db.profIntroLinks.insert_one(links_dict)
            return jsonify({"link": res_link})
    return jsonify({"error": None})


@main.route('/get_course_description/<course_section>')
def get_course_description(course_section):
    description_url = "https://catalog.utdallas.edu/2019/graduate/courses/" + course_section
    try:
        resp = requests.get(description_url)
        selector = html.etree.HTML(resp.text)
        text_list = selector.xpath('''.//div[@id="bukku-page"]/p//text()''')
    except:
        return None
    return jsonify("".join(text_list))


@main.before_app_first_request
def before_first_request():
    global TIMEDELTA, collection, db, REDIS_HOST, REDIS_PORT, REDIS_UPDATE_TIME_KEY, REDIS_UPDATE_NEXT_TIME_KEY, TERM_LIST
    TIMEDELTA = current_app.config.get('TIMEDELTA')
    TERM_LIST = current_app.config.get('TERM_LIST')
    session['DATA_SOURCE'] = TERM_LIST[0]  # first term
    session['search_tool'] = False  # search tool status marker True: hide False: not hide
    REDIS_UPDATE_TIME_KEY = current_app.config.get('REDIS_UPDATE_TIME_KEY')
    REDIS_UPDATE_NEXT_TIME_KEY = current_app.config.get('REDIS_UPDATE_NEXT_TIME_KEY')
    MONGO_HOST = current_app.config.get('MONGO_HOST')
    MONGO_PORT = current_app.config.get('MONGO_PORT')
    REDIS_HOST = current_app.config.get('REDIS_HOST')
    REDIS_PORT = current_app.config.get('REDIS_PORT')
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client.Coursebook
    collection = db.CourseForSearch


@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@main.route('/findrate/<name>')
def findrate(name):
    pk_id, reason = getRateId(name)
    if not pk_id:
        # logging.INFO(reason)
        return redirect('https://www.ratemyprofessors.com/search.jsp?query=%s' % name)

    return redirect('https://www.ratemyprofessors.com/ShowRatings.jsp?tid=%s' % pk_id)


@main.route('/changesource/<source>')
def changesource(source):
    session['DATA_SOURCE'] = source
    data = list(collection.find({"class_term": source}, {"_id": 0}))
    return jsonify(data)


@main.route('/', methods=['GET', 'POST'])
def search():
    term = session.get("DATA_SOURCE", TERM_LIST[0])  # get term first

    item_list = ["class_title", "class_number", "class_section", "class_instructor",
                 "class_day", "class_start_time",
                 "class_end_time", "class_location"]  # "class_term", "class_status" 非前端筛选条件

    abbr_dict = {
        'ai': 'Artificial Intelligence',
        'ml': 'Machine Learning',
        'nlp': 'Natural Language Processing',
        'ca': 'Computer Architecture',
        'os': 'Operating System',
        'hci': 'Human Computer Interactions',
        'vr': 'Virtual Reality',
        'aos': 'Advanced Operating Systems',
    }

    item_dict = session.get('item_dict')
    if not item_dict:
        item_dict = {}
    item_dict_result = {}
    item_dict_result["class_term"] = term

    if request.method == 'POST':
        for each_item in item_list:
            if each_item in request.form and request.form[each_item]:
                item_dict[each_item] = request.form[each_item]
        if "class_title" in item_dict.keys():  # update class title based on addr dict
            if item_dict.get("class_title").lower() in abbr_dict.keys():
                item_dict.update(class_title=abbr_dict.get(item_dict.get("class_title").lower()))
        fuzzyquery = 1 if "fuzzyquery" in request.form else 0

        session['item_dict'] = item_dict
        session['fuzzyquery'] = fuzzyquery
        session['button'] = 'nowclass' if 'nowclass' in request.form else 'search'
        return redirect(url_for('main.search'))

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
    data_update_time, data_update_next_time = getDataupdatetime()
    if data_update_time or data_update_next_time:
        if data_update_time:
            data_update_time = datetime.datetime.strptime(data_update_time, "%Y-%m-%d %H:%M")
        if data_update_next_time:
            data_update_next_time = datetime.datetime.strptime(data_update_next_time, "%Y-%m-%d %H:%M")
    return render_template('search.html', data=courses_list, Filter=item_dict,
                           data_update_time=data_update_time, data_update_next_time=data_update_next_time)


@main.route('/graph/professor')
@main.route('/graph/professor/<professor>')
@main.route('/graph/course')
@main.route('/graph/course/<coursesection>')
@main.route('/graph/speed')
@main.route('/graph/speed/<term_num>')
def graph_pro(professor=None, coursesection=None, term_num=None):
    if not professor and not coursesection and not term_num:
        # TODO add global function to switch professor name to last name - first name or first name - last name
        if "graph/professor" in request.url:
            professor_dict_list = list(db.CourseForGraph.find({}, {"class_instructor": 1, "_id": 0}))
            if not professor_dict_list:
                return render_template("graph.html")

            def split_name(name):
                name_list = name.split(" ", 1)
                if len(name_list) == 1:
                    return name_list[0]
                else:
                    return name_list[1] + ", " + name_list[0]

            professor_set = set()
            [professor_set.add(split_name(name)) for prof_dict in professor_dict_list for name in
             prof_dict.get("class_instructor")
             if "Staff" not in name]
            professor_char_dict = defaultdict(list)
            [professor_char_dict[name[0]].append(name) for name in professor_set]
            professor_list_list = sorted([[k] + v for k, v in professor_char_dict.items()], key=lambda k: k[0])
            return render_template("graph.html", professor_list_list=professor_list_list)
        elif "graph/course" in request.url:
            cou_set = set()
            cou_dict_list_fin = []
            cou_dict_list = list(
                db.CourseForGraph.find({}, {"class_title": 1, "class_section": 1, "_id": 0}))
            for eachcou_dict in cou_dict_list:
                eachcou_dict["class_section"] = eachcou_dict.get("class_section").split(".")[0]
                if eachcou_dict["class_section"] not in cou_set:
                    cou_set.add(eachcou_dict["class_section"])
                    cou_dict_list_fin.append(eachcou_dict)
            return render_template("graph.html", cou_dict_list=cou_dict_list_fin)
        elif "graph/speed" in request.url:
            speed_dict_list = list(
                db.CourseForSpeed.find({}, {"_id": 0, "class_day": 0, "class_start_time": 0, "update_data": 0}))
            return render_template("graph.html", speed_dict_list=speed_dict_list)

    if term_num:
        term, num = term_num.split("_")
        speed_data_dict = get_speed_graph_data(class_term=term, class_number=num)
        return render_template('graph.html', speed_data_dict=speed_data_dict)

    if professor:
        coursesection_list, professor_json = get_professor_graph_data(professor)
        return render_template('graph.html',
                               professor_name=professor,
                               professor_json=professor_json)
    if coursesection:
        course_section, course_name, final_dict, professor_list = get_course_graph_data(coursesection)
        return render_template('graph.html',
                               course_section=course_section,
                               course_name=course_name,
                               course_json=final_dict)


def trans_utd(timestamp):
    utc_time = (datetime.datetime.utcfromtimestamp(timestamp) - datetime.timedelta(hours=TIMEDELTA)).strftime(
        "%Y-%m-%d %H:%M")
    return utc_time


def get_professor_graph_data(professor):
    if not list(db.CourseForGraph.find({"class_instructor": professor})):
        abort(404)
    term_dict_list = []
    coursesection_list = set()
    for eachterm in TERM_LIST:
        term_dict = {}
        course_dict_list = []
        all_course_list = list(
            db.CourseForGraph.find({"class_term": eachterm, "class_instructor": professor}, {"_id": 0}))
        if all_course_list:
            for eachcourse in all_course_list:
                course_dict = {}
                course_dict["name"] = eachcourse.get("class_title")
                class_section = eachcourse.get("class_section")
                coursesection_list.add(class_section.split(".")[0])
                course_dict["value"] = class_section.split(".")[0]
                course_dict_list.append(course_dict)
        term_dict["name"] = eachterm
        term_dict["children"] = course_dict_list
        term_dict_list.append(term_dict)
    professor_json = {"name": professor, "children": term_dict_list}
    return list(coursesection_list), professor_json


def get_course_graph_data(coursesection):
    all_course_list = list(db.CourseForGraph.find({"class_section": {"$regex": coursesection}}, {"_id": 0}))
    if not all_course_list:
        abort(404)
    else:
        course_name = all_course_list[0].get("class_title")
        course_section = coursesection.lower().replace(' ', '')

    term_dict = {}
    professor_list = []
    for eachterm in TERM_LIST:
        term_dict[eachterm] = []

    for eachcourse_dict in all_course_list:
        professorname_list = eachcourse_dict.get("class_instructor")
        professor_list += professorname_list
        term = eachcourse_dict.get("class_term")
        for eachprofessorname in professorname_list:
            temp_professorname_dict = {"name": eachprofessorname, "value": eachprofessorname}
            if not temp_professorname_dict in term_dict[term]:
                term_dict[term].append(temp_professorname_dict)

    final_list = []
    for eachterm in TERM_LIST:
        temp_final_dict = {"name": eachterm, "children": term_dict.get(eachterm)}
        final_list.append(temp_final_dict)
    final_dict = {"name": coursesection, "children": final_list}
    return course_section, course_name, final_dict, list(set(professor_list))


def get_speed_graph_data(**kwargs):
    # TODO think the structure of speed data
    if "class_number" in kwargs:
        if "class_term" in kwargs:
            speed_data = list(
                db.CourseForSpeed.find(
                    {"class_term": kwargs.get("class_term"), "class_number": kwargs.get("class_number")}, {"_id": 0}))
        elif "class_instructor" in kwargs:
            speed_data = list(db.CourseForSpeed.find(
                {"class_instructor": kwargs.get("class_instructor"), "class_number": kwargs.get("class_number")},
                {"_id": 0}))
        else:
            speed_data = list(db.CourseForSpeed.find({"class_number": kwargs.get("class_number")}, {"_id": 0}))
    elif "class_section" in kwargs:
        if "class_term" in kwargs:
            speed_data = list(
                db.CourseForSpeed.find(
                    {"class_term": kwargs.get("class_term"), "class_section": {"$regex": kwargs.get("class_section")}},
                    {"_id": 0}))
        elif "class_instructor" in kwargs:
            speed_data = list(db.CourseForSpeed.find(
                {"class_instructor": kwargs.get("class_instructor"),
                 "class_section": {"$regex": kwargs.get("class_section")}}, {"_id": 0}
            ))
        else:
            speed_data = list(
                db.CourseForSpeed.find({"class_section": {"$regex": kwargs.get("class_section")}}, {"_id": 0}))
    speed_data_dict = dict()
    for each_speed_data in speed_data:
        x_data = [trans_utd(each.get("timestamp")) for each in each_speed_data.get("update_data")]
        y_data = [each.get("percentage") * 100 for each in each_speed_data.get("update_data")]
        class_section = each_speed_data.get("class_section")
        class_term = each_speed_data.get("class_term")
        class_instructor = each_speed_data.get("class_instructor")
        class_title = each_speed_data.get("class_title")
        if class_term not in speed_data_dict:
            speed_data_dict.update(
                {class_term: {class_section: {"x_data": x_data, "y_data": y_data, "class_title": class_title,
                                              "class_instructor": class_instructor}}})
        else:
            speed_data_dict[class_term].update(
                {class_section: {"x_data": x_data, "y_data": y_data, "class_title": class_title,
                                 "class_instructor": class_instructor}})
    return speed_data_dict


def get_grade_graph_data(course_section, **kwargs):
    prefix, section_num = course_section.split(" ")
    grade_graph_data_dict = defaultdict(list)
    if "prof" in kwargs:
        prof_list = kwargs.get("prof").split(" ", 1)
        if len(prof_list) == 2:
            prof = prof_list[1] + ", " + prof_list[0]
        else:
            prof = kwargs.get("prof")
        grade_graph_data = list(
            db.utdgrades.find({"subj": prefix, "num": section_num, "prof": {"$regex": prof}}, {"_id": 0}))
    else:
        grade_graph_data = list(db.utdgrades.find({"subj": prefix, "num": section_num}, {"_id": 0}))
    for each_grade_graph_data in grade_graph_data:
        professor = each_grade_graph_data.get("prof")
        term = each_grade_graph_data.get("term")
        section = each_grade_graph_data.get("sect")
        grades = each_grade_graph_data.get("grades")
        for k, v in grades.items():
            grades[k] = int(v)
        term_section = term + " | " + course_section + " | " + section
        grade_graph_data_dict[professor].append({term_section: grades})
    for professor in grade_graph_data_dict:
        grade_graph_data_dict[professor].sort(
            key=lambda k: list(k.keys())[0], reverse=True)  # sort by section: 2019 Spring | CS 5333 | 001
    return grade_graph_data_dict


@main.route('/course/<coursesection>')
@main.route('/professor/<professor>')
def course(coursesection=None, professor=None):
    def grade_in(one_name, one_list, sec_or_prof):
        if sec_or_prof == "sec":
            for one in one_list:
                temp_list = one.split(" ", 1)
                if len(temp_list) == 2:
                    new_key = temp_list[1] + ", " + temp_list[0]
                else:
                    new_key = one
                if new_key in one_name:
                    return True
            return False
        else:
            return one_name in one_list

    def get_grade_dict_list(grade_data_dict, sem_dict_dict, mark):
        sem_dict = [
            {"semester": each.get('name'),
             "sections_or_profs": [each_each.get('value') for each_each in each.get('children')]} for
            each in sem_dict_dict.get("children")]

        prior_dict = dict()
        for sec_or_prof, grade in grade_data_dict.items():
            for sem in sem_dict:
                if grade_in(sec_or_prof, sem.get("sections_or_profs"), mark):
                    if sem.get("semester") in TERM_LIST[:2]:
                        if sec_or_prof not in prior_dict:
                            prior_dict[sec_or_prof] = {
                                "prof": sec_or_prof,
                                "grade": grade,
                                "badges": [sem.get("semester")],
                                "priority": int(sem.get("semester")[:2])
                            } if mark == "sec" else {
                                "section": sec_or_prof,
                                "prof": list(grade.keys())[0],
                                "grade": list(grade.values())[0],
                                "badges": [sem.get("semester")],
                                "priority": int(sem.get("semester")[:2])
                            }
                        else:
                            prior_dict[sec_or_prof]["badges"].append(sem.get("semester"))
                            prior_dict[sec_or_prof]["priority"] += int(sem.get("semester")[:2])
                        prior_dict[sec_or_prof]["priority"] += 2 if TERM_LIST.index(sem.get("semester")) == 0 else 1
                    else:
                        if sec_or_prof not in prior_dict:
                            prior_dict[sec_or_prof] = {
                                "prof": sec_or_prof,
                                "grade": grade,
                                "badges": [],
                                "priority": int(sem.get("semester")[:2])
                            } if mark == "sec" else {
                                "section": sec_or_prof,
                                "prof": list(grade.keys())[0],
                                "grade": list(grade.values())[0],
                                "badges": [],
                                "priority": int(sem.get("semester")[:2])
                            }
                        break
        return sorted(list(prior_dict.values()), key=lambda each: each.get("priority"), reverse=True)

    if coursesection:
        course_section, course_name, final_dict, professor_list = get_course_graph_data(coursesection)
        speed_data_dict = get_speed_graph_data(class_section=coursesection)
        grade_data_dict = get_grade_graph_data(coursesection)
        grade_dict_list = get_grade_dict_list(grade_data_dict, final_dict, "sec")
        return render_template("course.html",
                               course_section=course_section,
                               course_name=course_name,
                               course_json=final_dict,
                               speed_data_dict=speed_data_dict,
                               grade_dict_list=grade_dict_list)
    elif professor:
        # TODO 增加课程名称
        # TODO professor link 404
        coursesection_list, professor_json = get_professor_graph_data(professor)
        speed_data_dict = {each_section: get_speed_graph_data(class_section=each_section, class_instructor=professor)
                           for each_section in coursesection_list}
        speed_data_dict = {k: v for k, v in speed_data_dict.items() if v}
        grade_data_dict = {each_section: get_grade_graph_data(each_section, prof=professor) for each_section in
                           coursesection_list}
        grade_data_dict = {k: v for k, v in grade_data_dict.items() if v}
        grade_dict_list = get_grade_dict_list(grade_data_dict, professor_json, "prof")
        return render_template("professor.html",
                               professor_name=professor,
                               coursesection_list=coursesection_list,
                               professor_json=professor_json,
                               speed_data_dict=speed_data_dict,
                               grade_dict_list=grade_dict_list)
    else:
        abort(404)


@main.route('/comment')
@main.route('/comment/<professor>')
def comment(professor=None):
    if not professor:
        courses = list(db.CourseForGraph.find({}, {"_id": 0, "class_title": 0, "class_section": 0, "class_term": 0}))
        professor_set = set()
        for course in courses:
            for each_professor in course.get("class_instructor"):
                professor_set.add(each_professor)
        return render_template('comment.html', professor_list=list(professor_set))
    else:
        courses = list(
            db.CourseForGraph.find({"class_instructor": professor}, {"_id": 0, "class_term": 0, "class_instructor": 0}))
        section_set = set()
        title_set = set()
        section_title_set = set()
        for course in courses:
            section = course.get("class_section").split(".")[0]
            title = course.get("class_title")
            if section not in section_set and title not in title_set:
                section_set.add(section)
                title_set.add(title)
                section_title_set.add(section + "-" + title)
        return render_template('comment.html', professor_name=professor, section_title_list=list(section_title_set))

# @main.route('/jobinfo')
# def jobinfo():
#     job_filter, num = get_jobinfo_args()
#     if db.JobInfo.find(job_filter).count() - num <= 10:
#         return render_template('jobinfo.html')
#     else:
#         data = db.JobInfo.find(job_filter, {'_id': 0, 'name': 1, 'company': 1, 'city': 1, 'create_time': 1}).sort(
#             [{'create_time', -1}]).skip(num).limit(10)
#
#         return render_template('jobinfo.html', data=list(data), job_filter=job_filter)

# def get_jobinfo_args():
#     job_filter = {}
#
#     city_index = request.args.get('city')
#     city = city_dict.get(city_index)
#     if city:
#         job_filter['city'] = city
#
#     firm_index = request.args.get('firm')
#     firm = firm_dict.get(firm_index)
#     if firm:
#         job_filter['company'] = firm
#
#     num = request.args.get('num')
#     if not num:
#         num = 0
#     else:
#         num = int(num)
#     return job_filter, num
#
#
# @main.route('/jobinfodata')
# def jobinfodata():
#     job_filter, num = get_jobinfo_args()
#
#     data = db.JobInfo.find(job_filter, {'_id': 0, 'name': 1, 'company': 1, 'city': 1, 'create_time': 1}).sort(
#         [{'create_time', -1}]).skip(num).limit(10)
#     ifnext = not db.JobInfo.find(job_filter).count() - num <= 10
#     ifpre = num > 0
#     result = {'data': list(data), 'ifnext': ifnext, 'ifpre': ifpre}
#     return jsonify(result)
#
#
# city_dict = {
#     '1': '北京',
#     '2': '上海',
#     '3': '杭州',
#     '4': '深圳',
#     '5': '武汉',
# }
#
# firm_dict = {
#     '1': 'bytedance',
#     '2': 'baidu',
#     '3': 'bilibili',
# }
