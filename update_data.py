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
        self.collection = self.db.CourseForSearch
        self.collectionname = "CourseForSearch"
        # self.TERM_LIST = ['19S', '18F', '18U', '18S', '17F', '17U', '17S', '16F', '16U', '16S', '15F', '15U', '15S',
        #                   '14F', '14U', '14S', '13F', '13U', '13S', '12F', '12U', '12S', '11F', '11U', '11S', '10F',
        #                   '10U', '10S']
        # self.PREFIX_LIST = ['CS']  # CS/CE/EE/SE
        self.TERM_LIST = ['19S', '18F']
        self.PREFIX_LIST = ['CS', 'CE', 'EE', 'SE']

        self.justupdate = False
        self.insertdirectly = False

        self.search_information = {}
        self.course_dict_list = []

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

        for each_term in self.TERM_LIST:
            for each_prefix in self.PREFIX_LIST:
                resp = self.downloader(each_prefix, each_term)
                if not resp:
                    return
                log.logger.info("term: %s, prefix: %s, download OK" % (each_term, each_prefix))
                try:
                    self.parser(resp)
                    log.logger.info("term: %s, prefix: %s, parse OK" % (each_term, each_prefix))
                except:
                    return
            log.logger.info("term: %s download and parse ok" % each_term)

        if self.insertdirectly:
            try:
                self.collection.insert(self.course_dict_list)
                log.logger.info("insert directly complete")
            except:
                log.logger.error("insert directly error")
            return

        if not self.justupdate:  # renew all data
            try:
                self.db.temp.insert(self.course_dict_list)
            except:
                log.logger.debug('self.collection.insert_one fail')
                # self.db.temp.drop()
                log.logger.debug('db.temp not drop nothing happened')
                return
            log.logger.info("all data have inserted to temp collection")
            try:
                self.collection.drop()
                log.logger.info("the old collection has dropped")
            except:
                log.logger.error("the old collection drop fail")
                return
            try:
                self.db.temp.rename(self.collectionname)
                log.logger.info("db.temp has rename to %s" % self.collectionname)
            except:
                log.logger.error("db.temp rename %s error!" % self.collectionname)
                return
            try:
                redis_db = redis.StrictRedis.from_url("localhost")
                redis_db.set(self.data_update_time,
                             self.TIMENOW)  # write the time to redis 'localhost' 'data_update_time'
                log.logger.info("redis set OK")
            except:
                log.logger.error("redis set fail")
            return
        else:  # just update data
            for each_course_dict in self.course_dict_list:
                try:
                    self.collection.update_one({"class_term": each_course_dict.get("class_term"),
                                                "class_number": each_course_dict.get("class_number")},
                                               {"$set": each_course_dict},
                                               True)  # if not found insert
                except:
                    log.logger.error("data update fail, renew all data")
                    self.justupdate = False
                    self.update_database()
            log.logger.info("data update complete")
            try:
                redis_db = redis.StrictRedis.from_url("localhost")
                redis_db.set(self.data_update_time,
                             self.TIMENOW)  # write the time to redis 'localhost' 'data_update_time'
                log.logger.info("redis set OK")
            except:
                log.logger.error("redis set fail")
            return

    def downloader(self, perfix, term):
        base_uri = "https://coursebook.utdallas.edu/%s/term_%s" % (perfix, term)
        try:
            resp = requests.get(base_uri, headers=self.FAKE_HEADER)
        except requests.exceptions.ConnectionError as e:
            log.logger.error("Unable to download webpage.")
            log.logger.error("<%s>" % e)
            return False
        return resp

    def parser(self, resp):
        try:
            resp_url = resp.url
            resp_selector = html.etree.HTML(resp.text)
        except Exception as e:
            log.logger.debug("parser: etree fail: %s" % e)
            return False

        each_course_text_group = []
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
                'class_prefix': '',
                'class_section': '',
                'class_number': '',
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
            each_course_dict['class_prefix'] = eachclass_section_number[0].split(" ")[0]
            each_course_dict['class_section'] = eachclass_section_number[0]
            each_course_dict['class_number'] = eachclass_section_number[-1]
            # each_course_dict['_id'] = eachclass_section_number[-1]
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
            self.course_dict_list.append(each_course_dict)

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
