#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import setting, downloader, parser, db
from urllib.parse import urljoin


class Spider(object):
    def __init__(self, update_for_search=setting.UPDATE_FRO_SEARCH,
                 base_uri=setting.BASE_URI,
                 all_term=setting.ALL_TERM_LIST,
                 current_term=setting.CURRENT_TERM_LIST,
                 current_prefix=setting.CURRENT_PREFIX_LIST,
                 all_prefix=setting.ALL_PREFIX_LIST, header=None):
        self.downloader = None
        self.mongo_client = None
        self.redis_client = None
        self.base_uri = base_uri
        self.all_term = all_term
        self.all_prefix = all_prefix
        self.current_term = current_term
        self.current_prefix = current_prefix
        self.header = header
        self.update_for_search = update_for_search

    def init_downloader(self):
        self.downloader = downloader.Downloader()

    def init_db(self):
        DB = db.DB()
        self.redis_client = DB.get_redis()
        self.mongo_client = DB.get_mongo()

    def init_parser(self):
        self.parser = parser.Parser()

    def download(self, term, perfix, **kwargs):
        kwargs.update(self.header)
        if not self.downloader:
            self.init_downloader()
        if self.downloader:
            urls = []
            for each_term in term:
                for each_prefix in perfix:
                    url = self.base_uri.format(each_prefix, each_term)
                    urls.append(url)
                    resps = self.downloader.download(urls, **kwargs)
                    return resps
        else:
            print('init downloader failed.')
            return

    def parse(self, resps):
        if not self.parser:
            self.init_parser()
        if self.parser:
            self.parser.get_selector(resps)
            self.parser.parse_data()
        else:
            print('init parse failed.')
            return

    def update_data(self):
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
