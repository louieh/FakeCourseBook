#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __init__ import config as setting
from lxml import html
from log import logger
import time
import json


class Parser(object):
    def __init__(self, encoding=setting.ENCODING,
                 update_for_graph=setting.UPDATE_FOR_GRAPH,
                 update_for_search=setting.UPDATE_FOR_SEARCH,
                 update_for_speed=setting.UPDATE_FOR_SPEED,
                 col_name_search=setting.COLLECTION_NAME_FOR_SEARCH,
                 col_name_graph=setting.COLLECTION_NAME_FOR_GRAPH,
                 col_name_speed=setting.COLLECTION_NAME_FOR_SPEED,
                 ):
        self.encoding = encoding
        self.update_for_search = update_for_search
        self.update_for_graph = update_for_graph
        self.update_for_speed = update_for_speed
        self.col_name_search = col_name_search
        self.col_name_graph = col_name_graph
        self.col_name_speed = col_name_speed

    def get_selector(self, resp):
        try:
            resp.encoding = self.encoding
            resp_text = resp.text
            resp_text = json.loads(resp_text).get("sethtml").get("#sr")
            resp_text = resp_text.replace("\n", "").replace("\\", "")
            resp_url = resp.url
            resp_selector = html.etree.HTML(resp_text)
            return resp_selector
        except Exception as e:
            logger.error("parser: etree failed: {0}".format(repr(e)))
            return

    def parse_coursebook_tool(self, resps):
        for resp in resps:
            selector = self.get_selector(resp)
            courses = selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
            if not courses:
                logger.error("xpath changed? no courses")
                return
            for each_course in courses:
                try:
                    each_course_text = html.etree.tostring(each_course, method='html')
                    each_course_dict = {
                        'class_term': '',
                        'class_status': '',
                        'class_prefix': '',
                        'class_section': '',
                        'class_method': '',
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
                    each_course_selector = html.etree.HTML(each_course_text)
                    class_term_status = each_course_selector.xpath(
                        '''//td[1]//text()''')  # ['19S', 'Closed', '572/0.000293']

                    # class_term
                    class_term = class_term_status[0]
                    each_course_dict['class_term'] = class_term

                    # class_status
                    class_status = class_term_status[1]
                    each_course_dict['class_status'] = class_status
                    eachclass_section_number = each_course_selector.xpath(
                        '''//td[2]//text()''')  # ['CS 6375.004', '24869']
                    if setting.GRADUATE_LEVEL:
                        if eachclass_section_number[0].split(' ')[1][0] < '5':
                            continue

                    # class_prefix class_section class_number
                    each_course_dict['class_prefix'] = eachclass_section_number[0].split(" ")[0]
                    each_course_dict['class_section'] = eachclass_section_number[0]
                    # each_course_dict['class_number'] = eachclass_section_number[-1]
                    if len(eachclass_section_number) >= 2:
                        each_course_dict['class_method'] = eachclass_section_number[1]
                    # TODO each_course_dict['_id'] = eachclass_section_number[-1]

                    # class_title
                    class_title = each_course_selector.xpath('''//td[3]//text()''')
                    if class_title:
                        each_course_dict['class_title'] = class_title[0].replace("(3 Semester Credit Hours)",
                                                                                 "").replace(
                            "(1 Semester Credit Hours)", "").replace("(1-9 Credits)", "").replace(
                            "(1 Semester Credit Hour)", "").strip()

                    # class_instructor
                    class_instructor = each_course_selector.xpath(
                        '''//td[4]//text()''')  # ['Don Vogel', '\n, ', 'Stephen Perkins', '\n']
                    if class_instructor:
                        class_instructor = [x for x in class_instructor if '\n' not in x]
                        each_course_dict['class_instructor'] = class_instructor

                    # class_day class_time class_start_time class_end_time class_location
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

                    # class_isFull
                    class_ifFull = each_course_selector.xpath('''//td[6]/div/@title''')
                    if class_ifFull:
                        each_course_dict['class_isFull'] = class_ifFull[0]
                    else:
                        class_ifFull = each_course_selector.xpath('''//td[6]/div/@style''')
                        if class_ifFull:
                            class_ifFull = round(abs(int(class_ifFull[0].split(" ")[-2].replace("px", ""))) / 320 * 100,
                                                 2)
                            each_course_dict['class_isFull'] = str(class_ifFull) + "%"

                except Exception as e:
                    logger.error("parser failed: {0}".format(str(e)))
                    continue
                yield each_course_dict

    def get_update_for_search_it(self, resps):
        course_iter = self.parse_coursebook_tool(resps)
        for course_dict in course_iter:
            if course_dict.get('class_term') in setting.CURRENT_TERM_LIST:
                yield course_dict

    def get_update_for_graph_it(self, resps):
        course_iter = self.parse_coursebook_tool(resps)
        For_Graph_struc = setting.For_Graph_struc
        for course_dict in course_iter:
            temp_dict = dict()
            [temp_dict.update({each_key: course_dict.get(each_key)}) for each_key in For_Graph_struc]
            yield temp_dict

    def get_update_for_speed_it(self, resps):
        course_iter = self.parse_coursebook_tool(resps)
        For_Speed_struc = setting.For_Speed_struc
        timestamp = int(time.time())
        for course_dict in course_iter:
            if course_dict['class_term'] != setting.CURRENT_TERM_LIST[0]:
                continue
            temp_dict = dict()
            for each_key in For_Speed_struc:
                temp_dict[each_key] = int(
                    course_dict[each_key].split('%')[0]) / 100 if each_key == 'class_isFull' else course_dict[each_key]
            temp_dict['timestamp'] = timestamp
            yield temp_dict

    def parse_coursebook(self, resps, **kwargs):

        update_for_search_it = update_for_speed_it = update_for_graph_it = None

        if self.update_for_search:
            update_for_search_it = self.get_update_for_search_it(resps)
        if self.update_for_speed:
            update_for_speed_it = self.get_update_for_speed_it(resps)
        if self.update_for_graph:
            update_for_graph_it = self.get_update_for_graph_it(resps)

        final_dict = dict()
        if update_for_search_it:
            final_dict[self.col_name_search] = update_for_search_it
        if update_for_speed_it:
            final_dict[self.col_name_speed] = update_for_speed_it
        if update_for_graph_it:
            final_dict[self.col_name_graph] = update_for_graph_it

        return final_dict if final_dict else None

    def parse_prefix(self):
        all_prefix = []
        for selector in self.selectors:
            prefix_list = selector.xpath('''.//select[@id='combobox_cp']/option/text()''')
            for each_prefix in prefix_list:
                if '-' in each_prefix:
                    prefix = each_prefix.split('-')[0].strip()
                    all_prefix.append(prefix)
        return all_prefix
