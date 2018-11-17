#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update data and some search functions
"""

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


class CourseBook(object):
    def __init__(self):

        self.data_update_time = "data_update_time"
        self.client = MongoClient("localhost", 27017)
        self.db = self.client.Coursebook
        self.collection = None

        self.DATA_SOURCE_LIST = ['18f', '19s']
        self.PREFIX_LIST = ['cs', 'ce', 'ee', 'se']

        self.search_information = {}

        self.TIMENOW = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")

        self.FAKE_HEADER = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
            "DNT": "1",
            "Host": "coursebook.utdallas.edu",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        }

    def update_database(self):
        log.logger.info("Start time: %s" % self.TIMENOW)
        isSucceed_in_update_database = True
        for each_data_source in self.DATA_SOURCE_LIST:
            if each_data_source == '18f':
                self.collection = self.db.courses18fall_temp
                term = '18f'
            elif each_data_source == '19s':
                self.collection = self.db.courses19spring_temp
                term = '19s'
            else:
                log.logger.debug("update_database function:for each_data_source in DATA_SOURCE_LIST: Nothing to do.")
                return

            for each_prefix in self.PREFIX_LIST:
                if not self.insert_course(each_prefix, term):
                    log.logger.error("insert data fail")
                    isSucceed_in_update_database = False
                    break
                else:
                    log.logger.info("insert data OK")
        if isSucceed_in_update_database:
            timenow = self.TIMENOW
            try:
                redis_db = redis.StrictRedis.from_url("localhost")
                redis_db.set(self.data_update_time, timenow)  # write the time to redis 'localhost' 'data_update_time'
                log.logger.info("redis set OK")
            except:
                log.logger.error("redis set fail")
            try:
                self.db.courses18fall.drop()
                self.db.courses19spring.drop()
            except:
                log.logger.error("try to drop courses18fall/19spring fail")
            try:
                self.db.courses18fall_temp.rename('courses18fall')
                self.db.courses19spring_temp.rename('courses19spring')
            except:
                log.logger.error("try to rename collections fail")
        else:
            self.db.courses18fall_temp.drop()
            self.db.courses19spring_temp.drop()
            log.logger.error("--insert data fail--")
            return

    def insert_course(self, code, term):
        base_uri = "https://coursebook.utdallas.edu/%s/term_%s" % (code, term)
        try:
            resp = requests.get(base_uri, headers=self.FAKE_HEADER)
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
                    'class_term': '',
                    'class_status': '',
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
                class_term_status = each_course_selector.xpath(
                    '''//td[1]//text()''')  # ['19S', 'Closed', '572/0.000293']
                class_term = class_term_status[0]
                each_course_dict['class_term'] = class_term
                class_status = class_term_status[1]
                each_course_dict['class_status'] = class_status
                eachclass_section_number = each_course_selector.xpath('''//td[2]//text()''')  # ['CS 6375.004', '24869']
                if eachclass_section_number[0].split(' ')[1][0] < '5':
                    continue
                each_course_dict['class_section'] = eachclass_section_number[0]
                each_course_dict['class_number'] = eachclass_section_number[-1]
                each_course_dict['_id'] = eachclass_section_number[-1]
                class_title = each_course_selector.xpath('''//td[3]//text()''')
                if class_title:
                    each_course_dict['class_title'] = class_title[0].replace("(3 Semester Credit Hours)", "").replace(
                        "(1 Semester Credit Hours)", "").replace("(1-9 Credits)", "").replace(
                        "(1 Semester Credit Hour)", "")

                class_instructor = each_course_selector.xpath(
                    '''//td[4]//text()''')  # ['Don Vogel', '\n, ', 'Stephen Perkins', '\n']
                if class_instructor:
                    class_instructor = [x for x in class_instructor if '\n' not in x]
                    each_course_dict['class_instructor'] = class_instructor

                # --------------------
                class_day = each_course_selector.xpath(
                    '''//td[5]/div/span[@class="clstbl__resultrow__day"]//text()''')
                if class_day:
                    each_course_dict['class_day'] = class_day[0]

                    class_time_final = ''
                    class_time = each_course_selector.xpath(
                        '''//td[5]/div/span[@class="clstbl__resultrow__time"]//text()''')  # ['1:00pm - 3:45pm']
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
                    self.collection.insert_one(each_course_dict)  # TODO update method
                    # log.logger.info("insert ok")
                except:
                    log.logger.debug('insert_course function: Nothing to do.')
                    return False

        else:
            log.logger.error("resp_selector is None")
            return False
        return True

    def get_prefix(self):  # get all prefix of courses
        base_url = "https://coursebook.utdallas.edu/guidedsearch"
        resp = requests.get(base_url, headers=self.FAKE_HEADER)
        resp_selector = html.etree.HTML(resp.text)
        profix_list = resp_selector.xpath('''.//select[@id='combobox_cp']/option/text()''')
        for each_profix in profix_list:
            if '-' in each_profix:
                profix = each_profix.split('-')[0].strip()
                print(profix)

    # search

    # class_section

    def search_section(self, class_section, fuzzyQueryMark=True):
        if fuzzyQueryMark:
            self.search_information['class_section'] = re.compile(str(class_section), re.I)
        else:
            self.search_information['class_section'] = str(class_section)
        courses_list = list(self.collection.find(self.search_information))
        return courses_list

    # class_number
    def search_number(self, class_number, fuzzyQueryMark=True):
        if fuzzyQueryMark:
            self.search_information['class_number'] = re.compile(str(class_number), re.I)
        else:
            self.search_information['class_number'] = str(class_number)
        courses_list = list(self.collection.find(self.search_information))
        return courses_list

    # class_title
    def search_title(self, class_title):
        self.search_information['class_title'] = class_title
        courses_list = list(self.collection.find(self.search_information))

    # class_instructor
    def search_instructor(self, class_instructor):
        self.search_information['class_instructor'] = class_instructor
        courses_list = list(self.collection.find(self.search_information))

    # date and time
    def course_now(self):
        # 查找目前正在进行的课程
        week_now = time.strftime("%A", time.localtime(time.time()))
        time_now = (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime('%H:%M')
        self.search_information['class_day'] = re.compile(week_now, re.I)
        self.search_information['class_start_time'] = {"$lte": time_now}
        self.search_information['class_end_time'] = {"$gte": time_now}
        courses_list = list(self.collection.find(self.search_information))
        return courses_list

    # class_isFull
    def search_isFull(self, class_isFull):
        self.search_information['class_isFull'] = class_isFull
        courses_list = list(self.collection.find(self.search_information))

    # class_location
    def search_class_location(self, class_location):
        self.search_information['class_location'] = class_location
        courses_list = list(self.collection.find(self.search_information))
        return courses_list


newCourseBook = CourseBook()
newCourseBook.update_database()
