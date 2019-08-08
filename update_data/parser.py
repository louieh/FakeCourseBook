#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting
from lxml import html
from log import logger


class Parser(object):
    def __init__(self, encoding=setting.ENCODING):
        self.encoding = encoding

    def get_selector(self, resps):
        self.selectors = []
        if not isinstance(resps, list):
            resps = [resps]
        for resp in resps:
            try:
                resp.encoding = self.encoding
                resp_text = resp.text
                resp_url = resp.url
                resp_selector = html.etree.HTML(resp_text)
                self.selectors.append(resp_selector)
            except Exception as e:
                logger.error("parser: etree failed: {0},{1}".format(repr(e), resp_url))
                return
        return True

    def parse_prefix(self):
        all_prefix = []
        for selector in self.selectors:
            prefix_list = selector.xpath('''.//select[@id='combobox_cp']/option/text()''')
            for each_prefix in prefix_list:
                if '-' in each_prefix:
                    prefix = each_prefix.split('-')[0].strip()
                    all_prefix.append(prefix)
        return all_prefix

    def parse_data(self):
        final_dict_list = []
        each_course_text_group = []
        for selector in self.selectors:
            courses = selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
            if not courses:
                logger.error("xpath changed? no courses")
                return
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

            # class_term
            class_term = class_term_status[0]
            each_course_dict['class_term'] = class_term

            # class_status
            class_status = class_term_status[1]
            each_course_dict['class_status'] = class_status
            eachclass_section_number = each_course_selector.xpath('''//td[2]//text()''')  # ['CS 6375.004', '24869']
            if setting.GRADUATE_LEVEL:
                if eachclass_section_number[0].split(' ')[1][0] < '5':
                    continue

            # class_prefix class_section class_number
            each_course_dict['class_prefix'] = eachclass_section_number[0].split(" ")[0]
            each_course_dict['class_section'] = eachclass_section_number[0]
            each_course_dict['class_number'] = eachclass_section_number[-1]
            # TODO each_course_dict['_id'] = eachclass_section_number[-1]

            # class_title
            class_title = each_course_selector.xpath('''//td[3]//text()''')
            if class_title:
                each_course_dict['class_title'] = class_title[0].replace("(3 Semester Credit Hours)", "").replace(
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
            # pprint.pprint(each_course_dict)
            final_dict_list.append(each_course_dict)
        return final_dict_list
