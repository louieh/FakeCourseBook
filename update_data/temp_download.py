import json
import requests
from lxml import html
import redis
from pymongo import MongoClient
import datetime


# 1.直接下载coursebook入库
# 2.直接下载coursebook reportmonkey入库
# 3.下载coursebook获取reportmonkey key然后下载coursebook reportmonkey入库

# TODO 三个解析器
# TODO 两个下载器


class CouseBookSpider(object):
    def __init__(self):
        self.REDIS_HOST = "localhost"
        self.REDIS_PORT = 6379
        self.MONGO_HOST = "localhost"
        self.MONGO_PORT = 27017
        self.COLLECTION_NAME_FOR_SEARCH = 'CourseForSearch'
        self.COLLECTION_NAME_FOR_GRAPH = 'CourseForGraph'
        self.COLLECTION_NAME_FOR_SPEED = 'CourseForSpeed'
        self.DB_NAME = 'Coursebook'
        self.REDIS_KEY_FOR_SEARCH = 'search_data_update_time'
        self.REDIS_KEY_FOR_SEARCH_NEXT = 'search_data_next_update_time'
        self.REDIS_KEY_FOR_GRAPH = 'graph_data_update_time'
        self.REDIS_KEY_FOR_SPEED = 'speed_data_update_time'
        self.UPDATE_FOR_SEARCH = True
        self.UPDATE_FOR_GRAPH = False
        self.UPDATE_FOR_SPEED = False
        self.GRADUATE_LEVEL = True
        self.GET_DETAIL = False
        self.For_Speed_struc = ['class_title', 'class_term', 'class_number', 'class_section', 'class_instructor',
                                'class_isFull', 'class_day', 'class_start_time']  # timestamp
        self.For_Graph_struc = ['class_title', 'class_section', 'class_term', 'class_instructor', 'class_number']
        self.TIMENOW_UTC = lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    def downloader(self, url, header, datas):
        resps = []
        for data in datas:
            resp = requests.post(url, headers=header, data=data)
            resps.append(resp)
        return resps

    def downloader2(self, url, header):
        resp = requests.get(url, headers=header)
        return resp

    def get_selector(self, resp):
        resp_text = resp.text
        resp_text = json.loads(resp_text).get("sethtml").get("#sr")
        resp_text = resp_text.replace("\n", "").replace("\\", "")
        resp_selector = html.etree.HTML(resp_text)
        return resp_selector

    def reportmonkey_parser(self, resps, res_filter=None):
        res = []
        for resp in resps:
            selector = html.etree.HTML(resp.text)
            courses = selector.xpath('''.//div[@class="section__app"]//tbody/tr''')
            for each_course in courses:
                each_course_text = html.etree.tostring(each_course, method='html')
                each_course_dict = {

                }

    def parser(self, resps, res_filter=None):
        res = []
        for resp in resps:
            selector = self.get_selector(resp)
            courses = selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
            for each_course in courses:
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
                class_title = each_course_selector.xpath('''//td[4]//text()''')
                if class_title:
                    each_course_dict['class_title'] = class_title[0].replace("(3 Semester Credit Hours)",
                                                                             "").replace(
                        "(1 Semester Credit Hours)", "").replace("(1-9 Credits)", "").replace(
                        "(1 Semester Credit Hour)", "").strip()

                # class_instructor
                class_instructor = each_course_selector.xpath(
                    '''//td[5]//text()''')  # ['Don Vogel', '\n, ', 'Stephen Perkins', '\n']
                if class_instructor:
                    class_instructor = [x for x in class_instructor if '\n' not in x]
                    each_course_dict['class_instructor'] = class_instructor

                # class_day class_time class_start_time class_end_time class_location
                class_day = each_course_selector.xpath(
                    '''//td[6]/div/span[@class="clstbl__resultrow__day"]//text()''')
                if class_day:
                    each_course_dict['class_day'] = class_day[0]

                    class_time_final = ''
                    class_time = each_course_selector.xpath(
                        '''//td[6]/div/span[@class="clstbl__resultrow__time"]//text()''')  # ['1:00pm - 3:45pm']
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
                        '''//td[6]/div/div[@class="clstbl__resultrow__location"]//text()''')
                    if class_location:
                        each_course_dict['class_location'] = class_location[0]
                else:
                    class_location = each_course_selector.xpath('''//td[6]//text()''')
                    if class_location:
                        each_course_dict['class_location'] = class_location[0]

                # class_isFull
                class_ifFull = each_course_selector.xpath('''//td[7]/div/@title''')
                if class_ifFull:
                    each_course_dict['class_isFull'] = class_ifFull[0]
                else:
                    class_ifFull = each_course_selector.xpath('''//td[7]/div/@style''')
                    if class_ifFull:
                        class_ifFull = round(abs(int(class_ifFull[0].split(" ")[-2].replace("px", ""))) / 320 * 100,
                                             2)
                        each_course_dict['class_isFull'] = str(class_ifFull) + "%"
                if res_filter:
                    res.append({each: each_course_dict.get(each) for each in res_filter})
                else:
                    res.append(each_course_dict)
        return res

    def insert_mongo(self, host, port, db_name, col_name, data):
        mongo_client = MongoClient(host, port)
        db = mongo_client.get_database(db_name)
        col = db.get_collection(col_name)
        col.insert_many(data)

    def insert_redis(self, host, port, redis_key):
        pool = redis.ConnectionPool(host=host, port=port, decode_responses=True)
        redis_client = redis.Redis(connection_pool=pool)
        redis_client.set(redis_key, self.TIMENOW_UTC())

    def run(self):
        url = "https://coursebook.utdallas.edu/clips/clip-cb11-hat.zog"
        # url = "https://coursebook.utdallas.edu/reportmonkey/cb11-export/15a1ddfcfffb53b2d42499673e08557f55c36b6f"

        datas = [
            # "action=search&s%5B%5D=term_22s&s%5B%5D=cp_cs",
            # "action=search&s%5B%5D=term_21f&s%5B%5D=cp_cs",
            # "action=search&s%5B%5D=term_21u&s%5B%5D=cp_cs",
            "action=search&s%5B%5D=term_21s&s%5B%5D=cp_cs",
        ]

        header = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "PTGSESSID=f53e47ecbd7a0cf4cf7d0daafcbde5e2",
            "Host": "coursebook.utdallas.edu",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        }

        resps = self.downloader(url, header, datas)
        if self.UPDATE_FOR_SEARCH:
            res = self.parser(resps)
            self.insert_mongo(self.MONGO_HOST, self.MONGO_PORT, self.DB_NAME, self.COLLECTION_NAME_FOR_SEARCH, res)
        if self.UPDATE_FOR_GRAPH:
            res = self.parser(resps, self.For_Graph_struc)
            self.insert_mongo(self.MONGO_HOST, self.MONGO_PORT, self.DB_NAME, self.COLLECTION_NAME_FOR_GRAPH, res)
        self.insert_redis(self.REDIS_HOST, self.REDIS_PORT, self.REDIS_KEY_FOR_SEARCH)


if __name__ == "__main__":
    coursebook_spider = CouseBookSpider()
    coursebook_spider.run()
