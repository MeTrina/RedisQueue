# -*- coding: utf8 -*-
import multiprocessing
import requests
import sys
import threading
import time
from crud import MongoCRUD
from worker import Worker, Job, MultiThreadWorkerManager, MultiProcessWorkerManager

__author__ = 'augustsun'

class ApiKeyManager(object):
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.validate_keys = [k for k in api_keys]
        self.invalidate_keys = []
        self.over_limit_date = dict([(k, 0) for k in api_keys])
        self.stage = 0

    def available_key(self):
        # key分成两个接口，1，没有过限制的，2，全部都过了限制
        if len(self.validate_keys):
            self.stage = 0
            return self.validate_keys[0]
        elif self.stage == 0:
            self.stage = 1
            return self.validate_keys[-1]
        else:
            self.stage = 0
            return None

    def update_key_ok(self, api_key):
        if api_key in self.invalidate_keys:
            self.invalidate_keys.remove(api_key)
            self.validate_keys.append(api_key)
            self.validate_keys.sort(key=lambda x: self.over_limit_date.get(x, None))

    def update_key_over_limit(self, api_key):
        if api_key in self.validate_keys:
            self.validate_keys.remove(api_key)
            self.invalidate_keys.append(api_key)
            self.over_limit_date[api_key] = time.time()
            self.invalidate_keys.sort(key=lambda x: self.over_limit_date.get(x, 0))

class GooglePOIJob(Job):
    STATUS_INITED = 0
    STATUS_CRAWLED = 1
    STATUS_EXTRACTED = 2
    STATUS_SAVED = 3
    STATUS_ERROR_CRAWL = 100
    STATUS_ERROR_EXTRACT = 200
    STATUS_ERROR_SAVE = 300

    def __init__(self, base_url, status=STATUS_INITED, page_idx=0):
        Job.__init__(self)
        self.base_url = base_url
        self.status = status
        self.page_idx = page_idx
        self.new_urls = []
        pass

    def __str__(self):
        return 'base_url={},status={},new_urls={},page={},data={},error={}'.format(self.base_url,
                                                                                   self.status,
                                                                                   self.new_urls,
                                                                                   self.page_idx,
                                                                                   self.data,
                                                                                   self.error)

class JobURL(object):
    @classmethod
    def next_url(cls, base_url, next_page_token):
        return base_url

    @classmethod
    def location_and_type_url(cls, location, poi_type_list, radius=500):
        url = 'https://maps.googleapis.com/maps/api/place/search/json?sensor=false'
        url += '&language=zh_CN.TW'
        url += '&location=' + '%s,%s' % (location['lat'], location['lng'])
        url += '&radius=%s' % radius # 500 m
        url += '&types=%s' % '|'.join(poi_type_list)
        url += '&key=${API_KEY}'
        url += '&pagetoken='
        return url

class Crawler(Worker):
    def __init__(self, exit_flag, job_queue, done_queue, api_keys):
        Worker.__init__(self, exit_flag, job_queue, done_queue, -1)
        self.api_key_manager = ApiKeyManager(api_keys)

    def url_with_api_key(self, base_url, api_key):
        return base_url.replace('${API_KEY}', api_key)

    def do_job(self, job):
        base_url = job.base_url
        try:
            while True:
                api_key = self.api_key_manager.available_key()
                if api_key is None:
                    time.sleep(60)
                    continue
                url = self.url_with_api_key(base_url, api_key)
                r = requests.get(url)
                result = r.json()
                if result['status'] == 'OVER_QUERY_LIMIT':
                    self.api_key_manager.update_key_over_limit(api_key)
                    continue
                self.api_key_manager.update_key_ok(api_key)
                job.data['page_json'] = result
                job.data['page_content'] = r.content
                job.data['header'] = r.headers
                break

            if url is None or result['status'] != 'OK':
                job.status = GooglePOIJob.STATUS_ERROR_CRAWL
            else:
                job.status = GooglePOIJob.STATUS_CRAWLED
        except Exception as e:
            job.status = GooglePOIJob.STATUS_CRAWLED
            job.error = e
        print 'job', job
        return job

class Extractor(Worker):
    def __init__(self, exit_flag, job_queue, done_queue, api_key_manager):
        Worker.__init__(self, exit_flag, job_queue, done_queue, -1)
        self.crud = MongoCRUD()

    def do_job(self, job):
        if job.data['status'] == 1:
            json_data = job.data['page_json']
            results = json_data['result']
            self.crud.save_map_data_insert(results)
            if 'next_page_token' in json_data:
                page_token = json_data['next_page_token']
                next_url = JobURL.next_url(job.data['base_url'], page_token)
                page = job.page_idx + 1
                new_job = GooglePOIJob(next_url, page)
                job.new_urls.append(new_job)

class UrlCenter(Worker):
    def __init__(self, exit_flag, job_queue, done_queue, api_key_manager):
        Worker.__init__(self, exit_flag, job_queue, done_queue, -1)
        self.crud = MongoCRUD()

    def do_job(self, job):
        pass


exit_flag = multiprocessing.Value('i', 0, lock=True)  #Value函数返回一个shared memory包装类，其中包含一个ctypes对象
# crawl_job_queue = multiprocessing.Queue(10000)
crawl_job_queue = multiprocessing.Queue(10)
crawler_process_num = 1
crawler_thread_num = 5

# extract_queue = multiprocessing.Queue(10000)
extract_queue = multiprocessing.Queue(10)
extract_thread_num = 2

# save_url_queue = multiprocessing.Queue(10000)
save_url_queue = multiprocessing.Queue(10)
save_url_thread_num = 2

# from pydev import pydevd

# pydevd.settrace('192.168.11.198', port=9999, stdoutToServer=True, stderrToServer=True)

from conf import app_keys

# crawler_master = MultiProcessMultiThreadWorkerManager(exit_flag,
#                                                       crawl_job_queue, extract_queue,
#                                                       crawler_process_num, crawler_thread_num,
#                                                       Crawler, [app_keys])
#
# crawler_master = MultiProcessWorkerManager(exit_flag, crawl_job_queue, extract_queue,
#                                           crawler_process_num, Crawler, [app_keys])    #父进程
crawler_master = MultiThreadWorkerManager(exit_flag, crawl_job_queue, extract_queue,
                                          crawler_thread_num, Crawler, [app_keys])    #父线程
monitor_thread1 = threading.Thread(target=crawler_master.monitor_worker)  #初始化一个线程对象，传入函数crawler_master.monitor_worker
monitor_thread1.start() #启动线程
# monitor_thread1.join(2)  #tset: add to by aimee

def check_crawler_job():
    # crud = MongoCRUD()
    # while True:
    # all_locations = crud.read_all_locations()
    # le6 = ['food', 'restaurant', 'amusement_park', 'park', 'cafe', 'school', 'night_club',
    #        'zoo', 'shopping_mall', 'hair_care', 'museum']
    # for location in all_locations:
    #     url = JobURL.location_and_type_url(location, le6)
    #     job = GooglePOIJob(url)
    #     crawl_job_queue.put_nowait(job)
    url = 'https://maps.googleapis.com/maps/api/place/search/json?sensor=false' \
          '&language=zh-TW&location=25.11763232,121.5002&radius=400&types=]' \
          'rv_park|shoe_store|spa|stadium|storage|store|subway_station|synagogue|' \
          'taxi_stand|train_station|travel_agency|university|veterinary_care&key=${API_KEY}#&pagetoken='
    job = GooglePOIJob(url)
    crawl_job_queue.put_nowait(job)

    url = 'https://maps.googleapis.com/maps/api/place/search/json?sensor=false&language=zh-TW&location=25.11863232,121.5002&radius=400&types=rv_park|shoe_store|spa|stadium|storage|store|subway_station|synagogue|taxi_stand|train_station|travel_agency|university|veterinary_care&key=${API_KEY}&pagetoken='
    job = GooglePOIJob(url)
    crawl_job_queue.put_nowait(job)

    while True:
        time.sleep(2)
        print 'extract_queue_len', extract_queue.qsize()
        print 'crawler_queue_len', crawl_job_queue.qsize()

# pydevd.settrace('192.168.11.198', port=9999, stdoutToServer=True, stderrToServer=True)
# new_job_thread = threading.Thread(target=check_crawler_job)   #初始化一个线程对象，传入函数check_crawler_job
# new_job_thread.start() #启动线程
'''
try:
    time.sleep(100)
    print 'crawler_queue_len', crawl_job_queue.qsize()
    # new_job_thread.join(100)   #主线程阻塞等待子线程结束
                               #这句的意思是主线程将自我阻塞，然后等待new_job_thread表示的线程执行完毕再结束，如果没有这句，运行代码会立即结束
except:
    sys.exit(0)

    '''
