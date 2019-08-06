#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setting
import requests


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
                print('download url: {0}'.format(url))
                resp = self.session.get(url, headers=self.header)
            except requests.exceptions.ConnectionError as e:
                pass
                # log.logger.error('Unable to download the webpage: {0}'.format(url))
            except Exception as e:
                pass
                # log.logger.error('other error: {0}'.format(str(e)))
            if resp.status_code == 200:
                resps.append(resp)
            else:
                pass
                # log.logger.error('the status_code:{0}'.format(resp.status_code))

        return resps
