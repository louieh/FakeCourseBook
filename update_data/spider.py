#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __init__ import config as setting
import downloader, parser, db
from log import logger
from urllib.parse import urljoin


class Spider(object):
    def __init__(self, update_method=None,
                 update_for_graph=setting.UPDATE_FOR_GRAPH,
                 update_for_search=setting.UPDATE_FOR_SEARCH,
                 update_for_speed=setting.UPDATE_FOR_SPEED,
                 base_uri=setting.BASE_URI,
                 all_term=setting.ALL_TERM_LIST,
                 current_term=setting.CURRENT_TERM_LIST,
                 current_prefix=setting.CURRENT_PREFIX_LIST,
                 all_prefix=setting.ALL_PREFIX_LIST, header=None):
        self.update_method = update_method
        self.__downloader = None
        self.__db = None
        self.__parser = None
        self.base_uri = base_uri
        self.all_term = all_term
        self.all_prefix = all_prefix
        self.current_term = current_term
        self.current_prefix = current_prefix
        self.header = {} if header is None else header
        self.update_for_search = update_for_search
        self.update_for_graph = update_for_graph
        self.update_for_speed = update_for_speed

    def __init_downloader(self):
        self.__downloader = downloader.Downloader()

    def __init_db(self):
        self.__db = db.DB()
        r = self.__db.init_redis()
        m = self.__db.init_mongo()
        if not r or not m:
            return False
        else:
            return True

    def __init_parser(self):
        self.__parser = parser.Parser()

    def __download(self, urls=None, **kwargs):
        if not urls:
            logger.info('no urls...')
            return
        kwargs.update(self.header)
        if not self.__downloader:
            self.__init_downloader()
        if self.__downloader:
            logger.info('download start...')
            resps = self.__downloader.download(urls, **kwargs)
            return resps
        else:
            logger.error('init downloader failed.')
            return

    def __parse(self, resps, **kwargs):
        if not resps:
            logger.info('no resps')
            return
        if not self.__parser:
            self.__init_parser()
        if self.__parser:
            logger.info('download completed, parse start...')
            if self.update_method == 1:
                final_dict_list = self.__parser.parse_coursebook(resps)
                return final_dict_list
            else:
                logger.error('no match update method')
                return
        else:
            logger.error('init parse failed.')
            return

    def __insert_db(self, data, **kwargs):
        if not data:
            logger.info('no data to insert')
            return
        if not self.__db:
            self.__init_db()
        if self.__db:
            logger.info('parse completed, insert db start...')
            if self.update_method == 1:
                self.__db.insert_mongo_for_SG(data)
        else:
            logger.error('init db failed')
            return

    def update_data(self):
        logger.info('update start...')
        if not self.__db:
            if not self.__init_db():
                logger.error('init db error')
                return
        if self.update_method == 1:
            logger.info('update_method == 1')
            logger.info('update object: update for search: {0}, update for graph: {1}, update for speed: {2}'.format(
                self.update_for_search, self.update_for_graph, self.update_for_speed))
            urls = []
            if self.update_for_graph:
                prefix, term = (self.all_prefix, self.all_term)
            elif self.update_for_search:
                prefix, term = (self.current_prefix, self.current_term)
            elif self.update_for_speed:
                prefix, term = (self.current_prefix, [self.current_term[0]])
            else:
                logger.info('no update object')
                return
            logger.info("term, prefix: {0},{1}".format(term, prefix))
            for each_term in term:
                for each_prefix in prefix:
                    url = self.base_uri.format(each_prefix, each_term)
                    urls.append(url)
        else:
            logger.error('cannot find the update method')
            return
        resps = self.__download(urls)
        final_dict = self.__parse(resps)
        self.__insert_db(final_dict)

    def init_next_update_search(self, method=None):
        if method == 'add':
            if not self.__db:
                if not self.__init_db():
                    logger.error('init db error')
                    return
            self.__db.update_next_time_search()
        elif method == 'delete':
            pass
        # TODO
        else:
            return

    def get_prefix(self):  # get all prefix of courses
        base_url = setting.BASE_URL_FOR_PREFIX
        if not self.__downloader:
            self.__init_downloader()
        resp = self.__downloader.download(base_url)
        if not self.__parser:
            self.__init_parser()
        self.__parser.get_selector(resp)
        all_prefix = self.parser.parse_prefix()
        self.all_prefix = all_prefix if all_prefix else self.all_prefix
