# -*- coding:utf-8 -*-
__author__ = 'tea'
import requests
import time
from redis_queue import RedisQueues
from eu_queue import EuQueue
import threading
import multiprocessing
import sys
class Worker(object):
    def __init__(self,exit_flag,redis_que, eu_que ,max_job_num = 9):
        self.exit_flag = exit_flag
        self.redis_que = redis_que
        self.eu_que = eu_que
        self.max_job_num = max_job_num
    def is_alive(self):
        return False

    def do_works(self):
        # log.info('worker work now')
        print 'worker work now'
        #3.只要退出标记没有设定，每个worker最多job没超出限制，循环执行
        num = 0
        while not self.exit_flag.value and self.max_job_num > 0 and  num < self.max_job_num:
        #4.从queue中取出job,queue为空的话继续
        # add  by aimee
            item = self.redis_que.get() #job = self.job_queue.get(True, 5)
            if not item:
                break
            else:
                num += 1
                try:
                    self.do_job(item)
                except Exception as e:
                    print e
                # log.exception('process job failed, error=[{}]'.format(e))
                # log.info( 'exit worker, exit_flat=[{}], processed_job_num=[{}]'.format(self.exit_flag.value, num))

    def do_job(self, job):
        raise NotImplementedError


class CuWorker(Worker):
    def do_job(self, item):        # def run_work(self):
        items = dict()
        items['url'] = item
        items['crawl_begin_time'] = time.ctime()
        items = self.handle_url(item, items)
        items['crawl_end_time'] = time.ctime()
        self.eu_que.save_html(items)
        self.redis_que.task_done(item)

    def handle_url(self, url, items):
        try:  #考虑异常处理
            r = requests.get(url, timeout = 2)
        except requests.exceptions.RequestException as e:#在经过以 timeout 参数设定的秒数时间之后停止等待响应,并捕获异常
            #包含三种错误：
            # requests.exceptions.Timeout链接超时,
            # requests.exceptions.ConnectionError遇到网络问题（如：DNS查询失败、拒绝连接等）,
            # requests.exceptions.ConnectionError请求超过了设定的最大重定向次数
            print e
            sys.exit()  # exit the program
        url_content = r.text
        items['result'] = url_content
        url_header = r.headers
        items['header'] = url_header
        url_status_code = r.status_code
        items['status_code'] = url_status_code
        url_cookies = r.cookies
        items['cookies'] = url_cookies

        return items

class WorkerManager(object):
    """
    创建并监控worker状态，如果worker死掉，重新启动worker
    """

    def __init__(self, exit_flag, redis_que, eu_que , worker_num,
                 worker_constructor,constructor_arg = None, constructor_args=None, constructor_kwargs=None):
        self.exit_flag = exit_flag
        self.worker_num = worker_num
        self.redis_que = redis_que
        self.eu_que = eu_que
        self.worker_constructor = worker_constructor
        self.constructor_arg = constructor_arg
        self.constructor_args = constructor_args or []
        self.constructor_kwargs = constructor_kwargs or {}
        self.workers = []

    def new_worker(self):
        raise NotImplementedError

    def monitor_worker(self):   #父进程 ？ 实现什么功能
        #check_round = 99   #？？？这个参数有什么意义
        self.workers = []
        rupt_flag = 0
        while not self.exit_flag.value and rupt_flag < 10:
            rupt_flag = rupt_flag + 1
            #check_round += 1
           # if check_round % 100 == 0:
            #    check_round = 0
            self.workers = [worker for worker in self.workers if worker.is_alive()]
            while len(self.workers) < self.worker_num:
                worker = self.new_worker()
                worker.start()
                self.workers.append(worker)
            if not self.workers:
                break
            if self.redis_que.empty():   #added by aimee
               break
        self.exit_flag.value = 1
        #20.如果是flag改变的退出则等待所有进程执行完
        start = time.clock()
        while self.workers:  #??用作什么呢？
            time.sleep(10)
            print time.ctime()
            self.workers = [worker for worker in self.workers if worker.is_alive()]
        elapsed = (time.clock() - start)
        print("Time used:",elapsed)

class MultiThreadWorkerManager(WorkerManager):  #多
    def new_worker(self):
        print 'create thread'
        worker = self.worker_constructor(self.exit_flag, self.redis_que, self.eu_que, self.constructor_arg,
                                         *self.constructor_args, **self.constructor_kwargs)
        return threading.Thread(target=worker.do_works)

class MultiProcessWorkerManager(WorkerManager):
    def new_worker(self):
        worker = self.worker_constructor(self.exit_flag,  self.redis_que, self.eu_que,self.constructor_arg,
                                         *self.constructor_args, **self.constructor_kwargs)
        p = multiprocessing.Process(target=worker.do_works)
        return p
class MultiProcessMultiThreadWorkerManager(WorkerManager):
    def __init__(self, exit_flag, redis_que, eu_que, process_num, thread_num,
                 worker_constructor, constructor_arg, constructor_args=None, constructor_kwargs=None):
        WorkerManager.__init__(self, exit_flag, job_queue, done_queue,
                               process_num, worker_constructor, constructor_args,
                               constructor_kwargs)
        self.thread_num = thread_num

    def new_worker(self):
        def start_thread_manager():
            manager = MultiThreadWorkerManager(self.exit_flag, self.job_queue,
                                               self.done_queue,
                                               self.thread_num, self.worker_constructor,
                                               self.constructor_args, self.constructor_kwargs)
            manager.monitor_worker()
        return multiprocessing.Process(target=start_thread_manager)

if __name__ == '__main__':
    begin_time = time.clock()
    name_red = 'testA'
    name_eu = 'testB'
    redis_que = RedisQueues(name_red)
    eu_que = EuQueue(name_eu, redis_que)
    # eu_que = EuQueue()

    hosts = ["http://www.yahoo.com", "http://google.com","http://www.amazon.com","http://www.taobao.com/","http://www.apple.com","http://www.baidu.com"]
    #提取已经下载的页面里面的URL，保存至队列中
    for item in hosts:
        print "item1:",  item
        redis_que.put(item)

    exit_flag = multiprocessing.Value('i', 0, lock=True)
    print exit_flag
    worker_num = 1
    max_job_num = 1
    # crawler_mas = MultiThreadWorkerManager(exit_flag, redis_que, eu_que, worker_num, CuWorker, max_job_num)
    crawler_mas =  MultiProcessMultiThreadWorkerManager(exit_flag, redis_que, eu_que, worker_num, CuWorker, max_job_num)

    crawler_mas = MultiProcessWorkerManager(exit_flag, redis_que, eu_que, worker_num, CuWorker, max_job_num)
    crawler_mas.monitor_worker()

    print 'total_time:', time.clock() - begin_time
    # print eu_que.length()   ,'33'
    print 'redis_que.length',redis_que.length()

    # item = eu_que.get_html()
    # print type(item)
    # print item
#

