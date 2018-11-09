# -*- coding: UTF-8 -*-

"""
Monitor the courses and push information to the telegram
"""

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import requests
import datetime
from lxml import html

import telepot
import os

FAKE_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "DNT": "1",
    "Host": "coursebook.utdallas.edu",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
}

TeleClientID = "763882075"  # 154165889
TOKEN = os.environ['bot_TOKEN']


def initBot(TOKEN):
    bot = telepot.Bot(TOKEN)
    return bot


def downloader(section):
    url = "https://coursebook.utdallas.edu/%s/term_19s" % section
    resp = requests.get(url, headers=FAKE_HEADER)
    if not resp:
        print("error: cannot download the page")
        return
    each_course_text_group = []
    resp_selector = html.etree.HTML(resp.text)
    courses = resp_selector.xpath('''.//div[@class="section-list"]//tbody/tr''')
    if not courses:
        print("error: xpath changed? no courses")
        return
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
            class_section = eachclass_section_number[0]
        else:
            class_section = 0
        class_title = each_course_selector.xpath('''//td[3]//text()''')
        if class_title:
            class_title = class_title[0]
        else:
            class_title = "-"
        class_instructor = each_course_selector.xpath('''//td[4]//text()''')
        if class_instructor:
            if class_instructor[0] in professor_email_dict.keys():
                class_isFull = each_course_selector.xpath('''//td[6]/div/@title''')
                if class_isFull:
                    number = int(class_isFull[0].split("%")[0])
                    if number < 100 and class_ifopen == "Open":
                        email_list = professor_email_dict.get(class_instructor[0])
                        for eachemail in email_list:
                            text = "Class_terms: %s, Class_open: %s, Class_title: %s, Class_section: %s, Class_instructor: %s, isFull: %s" % (
                                class_terms, class_ifopen, class_title, class_section, class_instructor[0], number)
                            print(text)
                            bot.sendMessage(TeleClientID, text)
                            # sendmail(eachemail, text)
        else:
            print("error: no instructor")
            return


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


if __name__ == "__main__":
    TIMENOW = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    request_list = [
        {"section": "6375",
         "professor_email": {"Anurag Nagar": [""],
                             "Sriraam Natarajan": [""], }
         },
    ]
    bot = initBot(TOKEN)
    for each in request_list:
        section = each.get("section")
        each_course_text_group = downloader(section)
        if not each_course_text_group:
            print("downloader error.")
        else:
            professor_email_dict = each.get("professor_email")
            filtration(bot, each_course_text_group, professor_email_dict)
