#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting
import requests
from log import logger


class Downloader(object):
    def __init__(self, header=setting.FAKE_HEADER):
        self.header = header
        self.proxy = ''
        self.session = requests.Session()

    def download(self, urls, **kwargs):
        if not urls:
            return
        if not isinstance(urls, list):
            urls = [urls]
        header = kwargs.get('header', {})
        self.header.update(header)
        resps = []
        for url in urls:
            try:
                logger.info('download url: {0}'.format(url))
                resp = self.session.get(url, headers=self.header)
            except requests.exceptions.ConnectionError as e:
                logger.error('Unable to download the webpage: {0}'.format(url))
                return
            except Exception as e:
                logger.error('other error: {0}'.format(str(e)))
                return
            if resp.status_code == 200:
                resps.append(resp)
            else:
                logger.error('the status_code:{0}'.format(resp.status_code))
                return

        return resps
