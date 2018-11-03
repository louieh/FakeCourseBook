#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xlrd
import pprint
from pymongo import MongoClient
import requests
from lxml import html
import re
import time
import datetime
import logging
import redis
import log

data_update_time = "data_update_time"
client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = None

DATA_SOURCE_LIST = ['18f', '19s']
PREFIX_LIST = ['cs', 'ce', 'ee', 'se']

FAKE_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "DNT": "1",
    "Host": "coursebook.utdallas.edu",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
}


def get_prefix():  # get all prefix of courses
    base_url = "https://coursebook.utdallas.edu/guidedsearch"
    resp = requests.get(base_url, headers=FAKE_HEADER)
    resp_selector = html.etree.HTML(resp.text)
    profix_list = resp_selector.xpath('''.//select[@id='combobox_cp']/option/text()''')
    for each_profix in profix_list:
        if '-' in each_profix:
            profix = each_profix.split('-')[0].strip()
            print(profix)


def update_database(DATA_SOURCE_LIST, PREFIX_LIST):
    log.logger.info(
        "Start time: %s" % (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"))
    isSucceed_in_update_database = True
    for each_data_source in DATA_SOURCE_LIST:
        if each_data_source == '18f':
            collection = db.courses18fall_temp
            term = '18f'
        elif each_data_source == '19s':
            collection = db.courses19spring_temp
            term = '19s'
        else:
            log.logger.debug("update_database function:for each_data_source in DATA_SOURCE_LIST: Nothing to do.")
            return

        for each_prefix in PREFIX_LIST:
            if not insert_course(each_prefix, term, collection):
                log.logger.error("insert data fail")
                isSucceed_in_update_database = False
            else:
                log.logger.info("insert data OK")
    if isSucceed_in_update_database:
        timenow = (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime('%Y/%m/%d %H:%M')
        try:
            redis_db = redis.StrictRedis.from_url("localhost")
            redis_db.set(data_update_time, timenow)  # write the time to redis 'localhost' 'data_update_time'
            log.logger.info("redis set OK")
        except:
            log.logger.error("redis set fail")
        try:
            db.courses18fall.drop()
            db.courses19spring.drop()
        except:
            log.logger.error("try to drop courses18fall/19spring fail")
        try:
            db.courses18fall_temp.rename('courses18fall')
            db.courses19spring_temp.rename('courses19spring')
        except:
            log.logger.error("try to rename collections fail")
    else:
        db.courses18fall_temp.drop()
        db.courses19spring_temp.drop()
        log.logger.error("--insert data fail--")
        return


def insert_course(code, term, collection):
    base_uri = "https://coursebook.utdallas.edu/%s/term_%s" % (code, term)
    try:
        resp = requests.get(base_uri, headers=FAKE_HEADER)
        resp_selector = html.etree.HTML(resp.text)
    except requests.exceptions.ConnectionError as e:
        log.logger.error("Unable to download webpage.")
        log.logger.error("<%s>" % e)
        return False

    each_course_text_group = []
    if resp_selector is not None:
        courses = resp_selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
        if not courses:
            log.logger.error("xpath changed? no courses")
            return False
        for each_course in courses:
            each_course_text = html.etree.tostring(each_course, method='html')
            each_course_text_group.append(each_course_text)
        for each_course_text_ in each_course_text_group:
            each_course_dict = {
                'class_section': '',
                'class_number': '',
                '_id': '',
                'class_title': '',
                'class_instructor': '',
                'class_day': '',
                'class_time': '',
                'class_start_time': '',
                'class_end_time': '',
                'class_location': '',
                'class_isFull': '',
            }
            each_course_selector = html.etree.HTML(each_course_text_)
            eachclass_section_number = each_course_selector.xpath('''//td[2]//text()''')
            if eachclass_section_number[0].split(' ')[1][0] < '5':
                continue
            each_course_dict['class_section'] = eachclass_section_number[0]
            each_course_dict['class_number'] = eachclass_section_number[-1]
            each_course_dict['_id'] = eachclass_section_number[-1]
            class_title = each_course_selector.xpath('''//td[3]//text()''')
            if class_title:
                each_course_dict['class_title'] = class_title[0]
            class_instructor = each_course_selector.xpath('''//td[4]//text()''')
            if class_instructor:
                each_course_dict['class_instructor'] = class_instructor[0]

            # --------------------
            class_day = each_course_selector.xpath(
                '''//td[5]/div/span[@class="clstbl__resultrow__day"]//text()''')
            if class_day:
                each_course_dict['class_day'] = class_day[0]

                class_time_final = ''
                class_time = each_course_selector.xpath(
                    '''//td[5]/div/span[@class="clstbl__resultrow__time"]//text()''')
                if class_time:
                    class_time = class_time[0]
                for each_time in class_time.split("-"):
                    each_time = each_time.strip()
                    if 'am' in each_time:
                        class_time_final += each_time.replace("am", "") + '-'
                    if 'pm' in each_time:
                        if each_time.split(":")[0] == '12':
                            class_time_final += each_time.replace("pm", "") + '-'
                        else:
                            each_time_hour = str(int(each_time.split(":")[0]) + 12)
                            each_time_min = each_time.split(":")[-1].replace("pm", "")
                            class_time_final += (each_time_hour + ':' + each_time_min) + '-'
                each_course_dict['class_time'] = class_time_final[:-1]
                each_course_dict['class_start_time'] = each_course_dict['class_time'].split("-")[0]
                each_course_dict['class_end_time'] = each_course_dict['class_time'].split("-")[-1]
                class_location = each_course_selector.xpath(
                    '''//td[5]/div/div[@class="clstbl__resultrow__location"]//text()''')
                if class_location:
                    each_course_dict['class_location'] = class_location[0]
            else:
                class_location = each_course_selector.xpath('''//td[5]//text()''')
                if class_location:
                    each_course_dict['class_location'] = class_location[0]
            # --------------------------

            class_ifFull = each_course_selector.xpath('''//td[6]/div/@title''')
            if class_ifFull:
                each_course_dict['class_isFull'] = class_ifFull[0]
            # pprint.pprint(each_course_dict)
            try:
                collection.insert_one(each_course_dict)
                # log.logger.info("insert ok")
            except:
                log.logger.debug('insert_course function: Nothing to do.')
                return False

    else:
        log.logger.error("resp_selector is None")
        return False
    return True


# search

# class_section
search_information = {}


def search_section(class_section, fuzzyQueryMark=True):
    if fuzzyQueryMark:
        search_information['class_section'] = re.compile(str(class_section), re.I)
    else:
        search_information['class_section'] = str(class_section)
    courses_list = list(collection.find(search_information))
    return courses_list


# class_number
def search_number(class_number, fuzzyQueryMark=True):
    if fuzzyQueryMark:
        search_information['class_number'] = re.compile(str(class_number), re.I)
    else:
        search_information['class_number'] = str(class_number)
    courses_list = list(collection.find(search_information))
    return courses_list


# class_title
def search_title(class_title):
    search_information['class_title'] = class_title
    courses_list = list(collection.find(search_information))


# class_instructor
def search_instructor(class_instructor):
    search_information['class_instructor'] = class_instructor
    courses_list = list(collection.find(search_information))


# date and time
def course_now():
    # 查找目前正在进行的课程
    week_now = time.strftime("%A", time.localtime(time.time()))
    time_now = (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime('%H:%M')
    search_information['class_day'] = re.compile(week_now, re.I)
    search_information['class_start_time'] = {"$lte": time_now}
    search_information['class_end_time'] = {"$gte": time_now}
    courses_list = list(collection.find(search_information))
    return courses_list


# class_isFull
def search_isFull(class_isFull):
    search_information['class_isFull'] = class_isFull
    courses_list = list(collection.find(search_information))


# class_location
def search_class_location(class_location):
    search_information['class_location'] = class_location
    courses_list = list(collection.find(search_information))
    return courses_list


if __name__ == "__main__":
    update_database(DATA_SOURCE_LIST, PREFIX_LIST)
    # wb = xlrd.open_workbook('classnumbers.xlsx')
    # sh = wb.sheet_by_index(0)
    #
    # first_col = sh.col_values(0)
    # for each_number in first_col:
    #     if type(each_number) != str:
    #         code = int(each_number)
    #     else:
    #         code = each_number
    #     insert_course(code)
