#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting, downloader, parser, db
from urllib.parse import urljoin


class Spider(object):
    def __init__(self, update_for_search=setting.UPDATE_FRO_SEARCH,
                 base_uri=setting.BASE_URI,
                 all_term=setting.ALL_TERM_LIST,
                 current_term=setting.CURRENT_TERM_LIST,
                 current_prefix=setting.CURRENT_PREFIX_LIST,
                 all_prefix=setting.ALL_PREFIX_LIST, header=None):
        self.downloader = None
        self.db = None
        self.parser = None
        self.base_uri = base_uri
        self.all_term = all_term
        self.all_prefix = all_prefix
        self.current_term = current_term
        self.current_prefix = current_prefix
        self.header = {} if header is None else header
        self.update_for_search = update_for_search

    def init_downloader(self):
        self.downloader = downloader.Downloader()

    def init_db(self):
        self.db = db.DB()
        r = self.db.init_redis()
        m = self.db.init_mongo()
        if not r or not m:
            return False
        else:
            return True

    def init_parser(self):
        self.parser = parser.Parser()

    def download(self, term, prefix, **kwargs):
        kwargs.update(self.header)
        if not self.downloader:
            self.init_downloader()
        if self.downloader:
            urls = []
            print("term, prefix: {0},{1}".format(term, prefix))
            for each_term in term:
                for each_prefix in prefix:
                    url = self.base_uri.format(each_prefix, each_term)
                    urls.append(url)
            resps = self.downloader.download(urls, **kwargs)
            return resps
        else:
            print('init downloader failed.')
            return

    def parse(self, resps):
        if not resps:
            print('no resps')
            return
        if not self.parser:
            self.init_parser()
        if self.parser:
            self.parser.get_selector(resps)
            final_dict_list = self.parser.parse_data()
            if not self.db:
                self.init_db()
            self.db.insert_mongo(final_dict_list)
        else:
            print('init parse failed.')
            return

    def update_data(self):
        if not self.db:
            if not self.init_db():
                print('init db error')
                return
        if self.update_for_search:
            prefix = self.current_prefix
            term = self.current_term
        else:
            prefix = self.all_prefix
            term = self.all_term
        resps = self.download(prefix, term)
        self.parse(resps)

    def get_prefix(self):  # get all prefix of courses
        base_url = setting.BASE_URL_FOR_PREFIX
        if not self.downloader:
            self.init_downloader()
        resp = self.downloader.download(base_url)
        if not self.parser:
            self.init_parser()
        self.parser.get_selector(resp)
        all_prefix = self.parser.parse_prefix()
        self.all_prefix = all_prefix if all_prefix else self.all_prefix
