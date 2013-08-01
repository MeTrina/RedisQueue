# -*- coding:utf-8 -*-
__author__ = 'tea'
from redis_queue import RedisQueues
import json,re,sys
import time
import redis
from crud import MongoCRUD
from conf import types, app_keys
class EuQueue(object):
    def __init__(self,name,redis_que):
        self.crud = MongoCRUD()
        self.keys_count = app_keys
        self.keys = app_keys.keys()
        self.key_begin = self.app_keys_pop()
        # self.key = app_keys_count(self.key_begin)
        self.redis_queue = redis_que
        self.name = name
        self.db = redis.Redis()

    def app_keys_pop(self):
        if len(self.keys) > 0:
            key = self.keys.pop()
            return key
        else:
            print "*------*-*all app keys have been used*-*-----*"
            sys.exit()
    def app_keys_count(self, key):
        count  = self.keys_count[key]
        if count > 999:
            key = self.app_keys_pop()
            count  = self.keys_count[key]
        count  = count + 1
        self.keys_count[key] = count
        self.key_begin = key
        print self.key_begin
        print count
        return key


    def change_radius(self):
        radius = 500
        return radius

    def change_language(self):
        language = 'zh-TW'
        return language

    def get_url(self, location, type):
        print '*********'
        url = 'https://maps.googleapis.com/maps/api/place/search/json?sensor=false'
        url += '&language=%s' % self.change_language()
        url += '&location=' + '%s,%s' % (location['lat'], location['lng'])
        url += '&radius=%s' % self.change_radius() # 500 m
        url += '&types=%s' % '|'.join(type)
        url += '&key=%s' % self.app_keys_count(self.key_begin)
        url += '&pagetoken='
        return url
    def save_html(self, item):
        print "save html into eu_queue:", item
        self.db.rpush(self.name, item)
    def get_html(self):
        item = self.db.lpop(self.name)
        return item
    def parse_html_save(self, item):
    # Show the source
        time.sleep(2)
        josn_response = self.get_html()
        status = item['status']
        if status == 'OK':
            results = josn_response['results']
            # insert to mongo
            self.crud.save_html_insert(results)
            if 'next_page_token' in item:
                pagetoken = '&pagetoken=%s' % josn_response['next_page_token']
                url = re.sub(r'&pagetoken=.*', pagetoken, url)
                self.parse_html(url)
            else:
                pass
        elif status == 'OVER_QUERY_LIMIT':
            self.key = self.app_keys_pop()
            url = re.sub(r'&key=.*&pagetoken', '&key=%s&pagetoken' % self.key, url)
            self.parse_html(url)
        else:
            return
        '''
    def run(self):
        all_locations = self.crud.read_all_locations()
        if len(self.keys) > 0:
            for location in all_locations:
                for type in types:
                    url = self.get_url(location, type)
                    print url
                    self.parse_html(url)
                self.crud.update_location_status(location['_id'])
        else:
            print "*------*-*all app keys have been used*-*-----*"
            sys.exit()

      '''
if __name__ == '__main__':
    name_red = 'testA'
    redis_que = RedisQueues(name_red)
    # eu_que = EuQueue(redis_que)

