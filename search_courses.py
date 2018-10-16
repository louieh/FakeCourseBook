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

client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = db.courses


# todo 目前哪些教室有人在上课，哪些没有
# todo 查询某个教室当天课表，下一节什么课

def get_prefix():
    base_url = "https://coursebook.utdallas.edu/guidedsearch"
    resp = requests.get(base_url)
    resp_selector = html.etree.HTML(resp.text)
    profix_list = resp_selector.xpath('''.//select[@id='combobox_cp']/option/text()''')
    for each_profix in profix_list:
        if '-' in each_profix:
            profix = each_profix.split('-')[0].strip()
            print(profix)


def update_database(code):
    collection.drop()
    for each_code in code:
        insert_course(each_code)

def insert_course(code):
    base_uri = "https://coursebook.utdallas.edu/%s/term_18f" % code
    try:
        resp = requests.get(base_uri)
        resp_selector = html.etree.HTML(resp.text)
    except requests.exceptions.ConnectionError as e:
        print("Unable to download webpage.")
        print("<%s>" % e)

    each_course_text_group = []
    if resp_selector is not None:
        courses = resp_selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
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
                collection.insert(each_course_dict)
                print(1)
            except:
                print(0)


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
    a = ['cs', 'ce', 'ee', 'se']
    update_datebase(a)
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
