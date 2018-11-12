# -*- coding: UTF-8 -*-

"""
Monitor the courses and push information to the telegram
Infinite loop
"""

import os
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

import requests
from lxml import html
import telepot
from pymongo import MongoClient
import redis

# TODO redesign data structure
# TODO section number 不是唯一值: 添加cs专业前缀？
# TODO 增加对每个client包含的section与professor记录以便删除某个client

FAKE_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "DNT": "1",
    "Host": "coursebook.utdallas.edu",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
}

MainTeleClientID = "763882075"  # 154165889
# TOKEN = os.environ['bot_TOKEN']

redis_db = redis.StrictRedis.from_url("localhost")
TOKEN = str(redis_db.get("bot_TOKEN"), encoding="utf-8")
client = MongoClient("localhost", 27017)
db = client.Coursebook
collection = db.monit_list


def initBot(TOKEN):
    bot = telepot.Bot(TOKEN)
    return bot


def downloader(section):
    url = "https://coursebook.utdallas.edu/%s/term_19s" % section
    resp = requests.get(url, headers=FAKE_HEADER)
    if not resp:
        print("error: cannot download the page")
        return '01'
    each_course_text_group = []
    resp_selector = html.etree.HTML(resp.text)
    courses = resp_selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
    if not courses:
        print("error: xpath changed? no courses")
        return '02'
    for each_course in courses:
        each_course_text = html.etree.tostring(each_course, method='html')
        each_course_text_group.append(each_course_text)
    return each_course_text_group


def filtration(bot, each_course_text_group, professor_email_dict):
    for each_course_text_ in each_course_text_group:
        each_course_selector = html.etree.HTML(each_course_text_)
        class_open = each_course_selector.xpath('''//td[1]//text()''')
        class_terms = class_open[0]
        class_ifopen = class_open[1]  # Open/Closed
        eachclass_section_number = each_course_selector.xpath('''//td[2]//text()''')
        if eachclass_section_number:
            class_section = eachclass_section_number[0].split(" ")[1].split(".")[0]
        else:
            class_section = 0
        class_title = each_course_selector.xpath('''//td[3]//text()''')
        if class_title:
            class_title = class_title[0]
        else:
            class_title = "-"
        class_instructor = each_course_selector.xpath('''//td[4]//text()''')
        if class_instructor:
            class_instructor = class_instructor[0]
            if class_instructor in professor_email_dict.keys():
                class_isFull = each_course_selector.xpath('''//td[6]/div/@title''')
                if class_isFull:
                    number = int(class_isFull[0].split("%")[0])

                    # -------------6313: Min Chen-------------
                    if "6313" in class_section and class_instructor == "Min Chen" and number == 83:
                        continue
                    # ----------------------------------------

                    time = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
                    if number < 100 and class_ifopen == "Open":
                        TeleClientID_list = professor_email_dict.get(class_instructor)
                        for eachTeleClientID in TeleClientID_list:
                            text = "Class_terms: %s, Class_open: %s, Class_title: %s, Class_section: %s, Class_instructor: %s, isFull: %s, Time: %s" % (
                                class_terms, class_ifopen, class_title, class_section, class_instructor, number,
                                time)
                            print(text)
                            bot.sendMessage(eachTeleClientID, text)
                            update_remove(section, professor=class_instructor, TeleClientID=eachTeleClientID)
                            # sendmail(eachemail, text)
        else:
            print("error: no instructor")
            bot.sendMessage(MainTeleClientID, "error: no instructor.")
            return False


def sendmail(mailaddress, text):
    my_sender = ''
    my_pass = ''
    my_user = mailaddress

    def mail():
        ret = True
        try:
            msg = MIMEText(text, 'plain', 'utf-8')
            msg['From'] = formataddr(["test", my_sender])
            msg['To'] = formataddr(["test", my_user])
            msg['Subject'] = "Reminder"

            server = smtplib.SMTP("smtp.qq.com", 25)
            server.login(my_sender, my_pass)
            server.sendmail(my_sender, [my_user, ], msg.as_string())
            server.quit()
        except Exception:
            ret = False
        return ret

    ret = mail()
    if ret:
        print("OK.")
    else:
        print("Fail.")


def update_insert(section, professor, TeleClientID):
    if list(collection.find({"section": section})):
        try:
            collection.update({
                "section": section}, {
                "$addToSet": {
                    "professor_email." + professor: TeleClientID
                }
            })
        except:
            print(
                "update insert section: %s, professor: %s, TeleClientID: %s fail" % (section, professor, TeleClientID))
            return False
        print("update insert section: %s, professor: %s, TeleClientID: %s OK" % (section, professor, TeleClientID))
        return True
    else:
        try:
            collection.insert_one({
                "section": section,
                "_id": section,
                "professor_email": {
                    professor: [TeleClientID]
                }
            })
        except:
            print("insert section: %s, professor: %s, TeleClientID: %s fail" % (section, professor, TeleClientID))
            return False
        print("insert section: %s, professor: %s, TeleClientID: %s fail" % (section, professor, TeleClientID))
        return True


def update_remove(section, **kw):
    if not list(collection.find({"section": section})):
        print("There is no section %s" % section)
        return False
    if not kw:  # section only
        try:
            collection.remove({"section": section})
        except:
            print("remove section: %s fail" % section)
            return False
        print("remove section: %s OK" % section)
        return True
    elif "professor" in kw.keys() and "TeleClientID" not in kw.keys():  # section + professor
        try:
            collection.update({"section": section}, {
                "$unset": {
                    "professor_email." + kw.get("professor"): 1
                }
            })
            if not list(collection.find({"section": section}))[0].get(
                    "professor_email"):  # if professor of the section is None, remove the section
                update_remove(section)
        except:
            print("remove section: %s professor: %s fail" % (section, kw.get("professor")))
            return False
        print("remove section: %s professor: %s OK" % (section, kw.get("professor")))
        return True
    elif "professor" in kw.keys() and "TeleClientID" in kw.keys():  # section + professor + TeleClientID
        try:
            collection.update({"section": section}, {
                "$pull": {
                    "professor_email." + kw.get("professor"): kw.get("TeleClientID")
                }
            })
            if not list(collection.find({"section": section}))[0].get("professor_email").get(kw.get(
                    "professor")):  # if TeleClientID of the professor of the section if None, remove the professor
                update_remove(section, professor=kw.get("professor"))
        except:
            print("remove TeleClientID: %s from professor: %s and section: %s fail" % (
                kw.get("TeleClientID"), kw.get("professor"), section))
            return False
        print("remove TeleClientID: %s from professor: %s and section: %s OK" % (
            kw.get("TeleClientID"), kw.get("professor"), section))
        return True
    elif "professor" not in kw.keys() and "TeleClientID" in kw.keys():  # section + TeleClientID
        try:
            tempdata = list(collection.find({"section": section}))[0]
            professor_dict = tempdata.get("professor_email")
            for eachprofessor in professor_dict:
                update_remove(section, professor=eachprofessor, TeleClientID=kw.get("TeleClientID"))
        except:
            print("remove TeleClientID: %s from section: %s fail" % (kw.get("TeleClientID")), section)
            return False
        print("remove TeleClientID: %s from section: %s OK" % (kw.get("TeleClientID")), section)
        return True


def removeClient(TeleClientID):  # the function should be improved
    section_list = list(collection.find({}))
    if not section_list:
        print("no section")
        return False
    for eachsection in section_list:
        section = eachsection.get("section")
        update_remove(section, TeleClientID=TeleClientID)


def initdata():
    collection.drop()
    request_list = [
        {"section": "6375",
         "_id": "6375",
         "professor_email": {
             "Anurag Nagar": ["763882075"],
             "Sriraam Natarajan": ["763882075"],
             "Gautam Kunapuli": ["763882075"],
         }
         },
        {
            "section": "6313",
            "_id": "6313",
            "professor_email": {
                "Min Chen": ["763882075"],
            }
        },
        {
            "section": "6363",
            "_id": "6363",
            "professor_email": {
                "Ramaswamy Chandrasekaran": ["763882075"],
                "Sergey Bereg": ["763882075"],
                "Balaji Raghavachari": ["763882075"],
                "Kyle Fox": ["763882075"],
            }
        }
    ]
    for eachrequest in request_list:
        collection.insert_one(eachrequest)


if __name__ == "__main__":

    # initdata()
    # update_insert("6313", "Gupta", "2352")
    # update_remove("6313", professor="Kyle Fox", TeleClientID="123")

    bot = initBot(TOKEN)
    Download_fail_num = 0  # count the number of download fail, try 3 times.
    while 1:
        ifDownload_fail = False
        xpatherror = False
        request_list = list(collection.find({}))
        if not request_list:
            bot.sendMessage(MainTeleClientID, "There is no any section, system stop.")
            break
        TIMENOW = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
        print(TIMENOW)
        hour = int(TIMENOW.split(" ")[1].split(":")[0])
        if hour >= 8 and hour <= 19:
            for each_request in request_list:
                section = each_request.get("section")
                each_course_text_group = downloader(section)
                if each_course_text_group == '01':
                    print("downloader error.")
                    bot.sendMessage(MainTeleClientID, "Download fail: %s" % section)
                    ifDownload_fail = True
                elif each_course_text_group == '02':
                    print("xpath error.")
                    bot.sendMessage(MainTeleClientID, "xpath error: %s system stop" % section)
                    xpatherror = True
                    break
                else:
                    ifDownload_fail = False
                    professor_email_dict = each_request.get("professor_email")
                    res = filtration(bot, each_course_text_group, professor_email_dict)
                time.sleep(3)
        if xpatherror:
            break
        if ifDownload_fail:
            Download_fail_num += 1
        if Download_fail_num >= 3:
            bot.sendMessage(MainTeleClientID, "The number of download fail is more than 3 times, system stop.")
            break
        time.sleep(600)
