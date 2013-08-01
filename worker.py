# -*- coding: utf8 -*-
import logging  #logging模块给运行中的应用提供了一个标准的信息输出接口, 它可以把输出信息输出到所有类文件的对象中去
import multiprocessing
import threading  #threading 模块允许程序员创建和管理线程
import time
import Queue  #Queue 模块允许用户创建一个可以用于多个线程之间共享数据的队列数据结构

__author__ = 'augustsun'
log = logging.getLogger(__name__)


class Job(object):
    def __init__(self):
        self.error = None
        self.data = dict()
        self.result = None


class Worker(object):
    def __init__(self, exit_flag, job_queue, done_queue, max_job_num = 9):
        self.exit_flag = exit_flag
        self.job_queue = job_queue
        self.done_queue = done_queue
        self.max_job_num = max_job_num
        # print "q111"

    def is_alive(self):
        return False

    def do_works(self):
        # log.info('worker work now')
        print 'worker work now'
        #3.只要退出标记没有设定，每个worker最多job没超出限制，循环执行
        num = 0
        while not self.exit_flag.value and (self.max_job_num < 0 or num < self.max_job_num):
            #4.从queue中取出job,queue为空的话继续
            # add  by aimee
            if self.max_job_num < 0:
                # print "max_job_max < 0 . quit!"
                break
            # to 2013.7.18
            try:
                # job = self.job_queue.get(True, 1000)
                # print "size:", self.job_queue.qsize()
                job = self.job_queue.get(True, 5)
                # print 'job==', job
            except Queue.Empty:
                continue
                #5.job数量+1
            num += 1
            try:
                print done_job
                done_job = self.do_job(job)
                print done_job
                done_job.error = None
                self.done_queue.put_nowait(done_job)  #??
            except Exception as e:
                # log.exception('process job failed, error=[{}]'.format(e))
                print e
                job.error = e
                self.done_queue.put_nowait(job)
        # log.info(
        #     'exit worker, exit_flat=[{}], processed_job_num=[{}]'.format(self.exit_flag.value, num))

    def do_job(self, job = None):
    # def do_job(self, job):  #add to aimee
        raise NotImplementedError


class WorkerManager(object):
    """
    创建并监控worker状态，如果worker死掉，重新启动worker
    """

    def __init__(self, exit_flag, job_queue, done_queue, worker_num,
                 worker_constructor, constructor_args=None, constructor_kwargs=None):
        self.exit_flag = exit_flag
        self.worker_num = worker_num
        self.job_queue = job_queue
        self.done_queue = done_queue
        self.worker_constructor = worker_constructor
        self.constructor_args = constructor_args or []
        self.constructor_kwargs = constructor_kwargs or {}
        self.workers = []
        # print "a1"
        # print "exit_flag.value :", self.exit_flag.value
        # print "worker_num :" , self.worker_num

    def new_worker(self):
        # print "b1"
        raise NotImplementedError

    def monitor_worker(self):   #父进程 ？ 实现什么功能
        # print "a2"
        check_round = 99   #？？？这个参数有什么意义
        self.workers = []
        xt = 1
        while not self.exit_flag.value and xt < 5:
            # print "xt",xt
            check_round += 1
            if check_round % 100 == 0:
                check_round = 0
                # print "workers:" ,len(self.workers)
                self.workers = [worker for worker in self.workers if worker.is_alive()]
                # print "workers1 :","\n", self.workers
                while len(self.workers) < self.worker_num:
                    # print "workers2 :",'\n', self.workers
                    worker = self.new_worker()
                    # print "worker :",'\n', worker
                    worker.start()
                    self.workers.append(worker)
                if not self.workers:
                    # print "xt!"
                    break
                    # time.sleep(1)
                xt = xt +1
        # print  "c1"
        self.exit_flag.value = 1
        #20.如果是flag改变的退出则等待所有进程执行完
        ti_flag = 1
        while self.workers:
            time.sleep(1)
            print time.ctime()
            self.workers = [worker for worker in self.workers if worker.is_alive()]
            # print "self.workers", self.workers
            print ti_flag
            ti_flag = ti_flag + 1


class MultiThreadWorkerManager(WorkerManager):  #多
    def new_worker(self):
        # print "b2"
        print 'create thread'
        worker = self.worker_constructor(self.exit_flag, self.job_queue, self.done_queue,
                                         *self.constructor_args, **self.constructor_kwargs)
        return threading.Thread(target=worker.do_works)


class MultiProcessWorkerManager(WorkerManager):
    def new_worker(self):
        # print "b3 : new_worker"
        worker = self.worker_constructor(self.exit_flag, self.job_queue, self.done_queue,
                                         *self.constructor_args, **self.constructor_kwargs)
        p = multiprocessing.Process(target=worker.do_works)
        return p


class MultiProcessMultiThreadWorkerManager(WorkerManager):
    def __init__(self, exit_flag, job_queue, done_queue, process_num, thread_num,
                 worker_constructor, constructor_args=None, constructor_kwargs=None):
        WorkerManager.__init__(self, exit_flag, job_queue, done_queue,
                               process_num, worker_constructor, constructor_args,
                               constructor_kwargs)
        # print "a3"
        self.thread_num = thread_num

    def new_worker(self):
        # print "b4 new_worker "
        def start_thread_manager():
            manager = MultiThreadWorkerManager(self.exit_flag, self.job_queue,
                                               self.done_queue,
                                               self.thread_num, self.worker_constructor,
                                               self.constructor_args, self.constructor_kwargs)
            manager.monitor_worker()
            # print "a4"

        return multiprocessing.Process(target=start_thread_manager)


class EchoWorker(Worker):
    def do_job(self, job):
        # print "a5"
        import pprint
        pprint.pprint(job)
        return job

exit_flag = multiprocessing.Value('i', 0, lock=True)
print exit_flag
worker_num = 5
# job_queue = multiprocessing.Queue(10000)
# done_queue = multiprocessing.Queue(10000)
job_queue = multiprocessing.Queue(10)
done_queue = multiprocessing.Queue(10)
job = Job()
job.hello = 'world'
job_queue.put_nowait(job)
max_job_num = 3
# multi_process_manager_master = MultiProcessMultiThreadWorkerManager(exit_flag,
#                                                                     job_queue, done_queue,
#                                                                     worker_num, 2,worker_num
#                                                                     EchoWorker)
# multi_process_manager_master.monitor_worker()
crawler_mas = MultiThreadWorkerManager(exit_flag, job_queue,done_queue,worker_num,EchoWorker)
crawler_mas.monitor_worker()
