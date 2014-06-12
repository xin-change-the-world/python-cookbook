#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第九章 进程、线程和同步
# Auther：张广欣
# Date：2014-06-12
#
#
'''
'''
在Python中通过增加线程来提速往往不是一个好的策略。原因就在于全局解释器锁（Global Interpreter Lock, GIL）
它被用来保护Python的内部数据结构。在一个线程能够安全的访问Python对象之前，它必须持有这个所。如果没有这个锁，
即使是最简单的操作（比如整数加法）都会失败。因此，只有带有GIL的线程能够操纵Python对象或者调用Python/C API函数
#asyncore
#Twisted
GIL最大的优势是它使得用C编写Python扩展成为一件容易的事情
使用锁的形式几乎是不变的，大概是这样：
somelock.acquire()
try:
    #需要锁的操作（尽量简短）
finally:
    somelock.release()
'''
'''
9.1 同步对象中的所有方法
'''
#你希望在多个线程中共享一个对象，但为了避免冲突，需要确保任何时间只有一个线程在对象中——可能还要除去一些你想手工调整锁定行为的方法
'''
inspect模块主要提供了四种用处：

(1).对是否是模块，框架，函数等进行类型检查。

(2).获取源码

(3).获取类或函数的参数的信息

(4).解析堆栈
'''
def wrap_callable(any_callable, before, after):
    '''用before/after调用将任何可调用体封装起来'''
    def _wrapped(*a, **kw):
        before()
        try:
            return any_callable(*a, **kw)
        finally:
            after()
    return _wrapped
import inspect
class GenericWrapper(object):
    '''将对象的所有方法用before/after调用封装起来'''
    def __init__(self, obj, before, after, ignore=()):
        #我们必须直接设置__dict__来绕过__setattr__;因此
        #我们需要重现下划线的名字
        clasname = 'GenericWrapper'
        self.__dict__['_%s__methods' % clasname] = {}
        self.__dict__['_%s__obj' % clasname] = obj
        for name, method in inspect.getmembers(obj, inspect.ismethod):
            if name not in ignore and method not in ignore:
                self.__methods[name] = wrap_callable(method, before, after)
    
    def __getattr__(self, name):
        try:
            return self.__methods[name]
        except KeyError:
            return getattr(self.__obj, name)

    def __setattr__(self, name, value):
        setattr(self.__obj, name, value)

#通过使用这些简单而通用的工具，同步变得容易了
class SynchronizedObject(GenericWrapper):
    '''封装一个对象及其所有方法，支持同步'''
    def __init__(self, obj, ignore=(), lock=None):
        if lock is None:
            import threading
            lock = threading.RLock()
        GenericWrapper.__init__(self, obj, lock.acquire, lock.release, ignore)


def test():
    import threading
    import time
    class Dummy(object):
        def foo(self):
            print 'hello from foo'
            time.sleep(1)
        def bar(self):
            print 'hello from bar'
        def baaz(self):
            print 'hello from baaz'
    tw = SynchronizedObject(Dummy(), ignore=['baaz'])
    threading.Thread(target=tw.foo).start()
    time.sleep(0.1)
    threading.Thread(target=tw.bar).start()
    time.sleep(0.1)
    threading.Thread(target=tw.baaz).start()
import time
test()
time.sleep(1)
'''
归功于同步机制，对bar的调用只有在对foo的调用完成之后才会发生。不过由于ignore=keyword
参数的指定，对baaz的调用绕过了同步并因此提前完成了，输出：
hello from foo
hello from baaz
hello from bar
本节的方案并没有封装对对象属性的直接访问（获得和设置）
如果你希望能够封装这种访问，需要在封装层的__getattr__和__setattr__特殊方法中使用try/finally枷锁形式
（一般只封装方法，已经被证明够用了）
'''

'''
9.2 终止线程
'''
#需要从外部结束一个线程，可是Python不允许一个线程强行杀死另一个线程，所以你得采用一种适当的受控终止的方式
#你不能杀死一个线程，你只能请求结束它。每个线程必须周期性的检查是否被要求结束，然后服从命令
import threading
class TestThread(threading.Thread):
    def __init__(self, name='TestThread'):
        """构造函数，设置初始值"""
        self.__stopevent = threading.Event()
        self._sleepperiod = 1.0
        threading.Thread.__init__(self, name=name)

    def run(self):
        """主控循环"""
        print "%s starts" % (self.getName(),)
        count = 0
        while not self.__stopevent.isSet():
            count += 1
            print "loop %d" % (count,)
            self.__stopevent.wait(self._sleepperiod)
        print "%s ends" % (self.getName(),)

    def join (self, timeout=None):
        """停止线程并等待其结束"""
        self.__stopevent.set()
        threading.Thread.join(self, timeout)

testthread = TestThread()
testthread.start()
import time
time.sleep(5.0)
testthread.join()
#你常常想在外部对线程施加一些控制，但杀死线程的能力却有点过头了。Python没有给你那个权力，它一次来迫使你更谨慎地设计你的线程系统
#本节的基本想法是在线程的主函数中使用一个循环。这个循环周期性滴检查threading.Event对象的状态。如果该对象被设置，线程就会结束，否则，它会一直等待。

'''
9.3 将Queue.Queue用作优先级队列
'''
#你很想使用Queue.Queue实例，因为它是最好的线程间通信的方式。不过，需要
#一点附加的功能，即给队列中的每一个子项都指定一个优先值。这样，拥有更低优先值（更急迫）的子项就会先于更高的优先值的子项被获取
#需要接管和封装Queue.Queue的put和get方法，在用put获得子项时给子项加上优先值和获取时间，在用get玻璃子项时则需要删除子项的所有附加信息
import Queue, heapq, time
class PriorityQueue(Queue.Queue):
    #初始化队列
    def _init(self, maxsize):
        self.maxsize = maxsize
        self.queue = []
    #返回队列子项的数目
    def _qsize(self):
        return len(self.queue)
    #检查队列是否为空
    def _empty(self):
        return not self.queue
    #检查队列是否已满
    def _full(self):
        return self.maxsize > 0 and len(self.queue) >= self.maxsize
    #给队列加入一个新项
    def _put(self, item):
        heapq.heapqpush(self.queue, item)
    #从队列中获取一项
    def _get(self):
        return heapq.heappop(self.queue)
    #屏蔽并封装Queue.Queue的put，使之允许priority参数
    def put(self, item, priority=0, block=True, timeout=None):
        decorated_item = priority, time.time(), item
        Queue.Queue.put(self, decorated_item, block, timeout)
    #屏蔽并封装Queue.Queue的get，以去除修饰
    def get(self, block=True, timeout=None):
        priority, time_posted, item = Queue.Queue.get(self, block, timeout)
        return item

'''
9.4 使用线程池
'''
#Queue.Queue是用来协调工作线程池的最简单和最有效率的方法。
import threading, Queue, time, sys
#全局变量（大写字母开头）
Qin = Queue.Queue()
Qout = Queue.Queue()
Qerr = Queue.Queue()
Pool = [ ]

def report_error():
    ''' 通过将错误信息放入Qerr来报告错误 '''
    Qerr.put(sys.exc_info()[:2])

def get_all_from_queue(Q):
    ''' 可以获取队列Q中所有项，无须等待 '''
    try:
        while True:
            yield Q.get_nowait()
    except Queue.Empty:
        raise StopIteration

def do_work_from_queue():
    ''' 工作线程的 获得一点工作， 做一点工作的主循环 '''
    while True:
        command, item = Qin.get() #这里可能会停止并等待
        if command == 'stop':
            break
        try:
            #模拟工作线程的工作
            if command == 'process':
                result = 'new' + item
            else:
                raise ValueError, 'Unknown command %r' % command
        except:
            #无条件except是对的，因为我们要报告所有错误
            report_error()
        else:
            Qout.put(result)

def make_and_start_thread_pool(number_of_threads_in_pool=5, daemons=True):
    ''' 创建一个N线程的池子，使所有线程成为守护线程，启动所有线程 '''
    for i in range(number_of_threads_in_pool):
        new_thread = threading.Thread(target=do_work_from_queue)
        new_thread.setDaemon(daemons)
        Pool.append(new_thread)
        new_thread.start()

def request_work(data, command='process'):
    ''' 工作请求在Qin中是形如（command，data）的数对 '''
    Qin.put((command, data))

def get_result():
    return Qout.get() #这里可能会停止并等待

def show_all_results():
    for result in get_all_from_queue(Qout):
        print 'Result:', result

def show_all_errors():
    for etyp, err in get_all_from_queue(Qerr):
        print 'Error:', etyp, err

def stop_and_free_thread_pool():
    #顺序是很重要的，首先要求所有线程停止
    for i in range(len(Pool)):
        request_work(None, 'stop')
    #然后，等待每个线程的终止
    for existing_thread in Pool:
        existing_thread.join()
    #清除线程池
    del Pool[:]

for i in ('_ba', '_be', '_bo'): request_work(i)
make_and_start_thread_pool()
stop_and_free_thread_pool()
show_all_results()
show_all_errors()
#发生错误的例子
for i in ('_ba', 7, '_bo'): request_work(i)
make_and_start_thread_pool()
stop_and_free_thread_pool()
show_all_results()
show_all_errors()

'''
9.5 以多组参数并行执行函数
'''
#需要用不同的多组参数来同时执行一个函数（这个函数可能是"I/O绑定的"）
#即它需要花费相当多的时间来完成输入输出操作，若非如此，同时执行没有多大用处
#我们对于每组参数使用一个线程。但为了获得好的性能，最好将线程的使用限定于一个有限的线程池：
import threading, time, Queue
class MultiThread(object):
    def __init__(self, function, argsVector, maxThreads=5, queue_results=False):
        self._function = function
        self._lock = threading.Lock()
        self._nextArgs = iter(argsVector).next 
        self._threadPool = [ threading.Thread(target=self._doSome) for i in range(maxThreads) ]
        
        if queue_results:
            self._queue = Queue.Queue()
        else:
            self._queue = None

    def _doSome(self):
        while True:
            self._lock.acquire()
            try:
                try:
                    args = self._nextArgs()
                except StopIteration:
                    break
            finally:
                self._lock.release()
            result = self._function(args)
            if self._queue is not None:
                self._queue.put((args, result))
    def get(self, *a, **kw):
        if self._queue is not None:
            return self._queue.put((args, result))
        else:
            raise ValueError, 'Not queueing results'
    def start(self):
        for thread in self._threadPool:
            time.sleep(0) #有必要给其他线程一个执行的机会
            thread.start()
    def join(self, timeout=None):
        for thread in self._threadPool:
            thread.join(timeout)
import random
def recite_n_times_table(n):
    for i in range(2, 11):
        print "%d * %d = %d" % (n, i, n * i)
        time.sleep(0.3 + 0.3*random.random())
mt = MultiThread(recite_n_times_table, range(2, 11))
mt.start()
mt.join()
print "Well done kids!"

'''
9.6 用简单的消息传递协调线程
'''
#你想编写一个多线程程序，在其中用一种简单而强大的消息传递模式，作为同步和通信的基础
#candygram模块允许你使用在语义上等同于Erlang的并行编程的Python对应物。为了使用candygram，你先要定义一个适合的类来规范你的线程功能
import candygram as cg 
class ExampleThread(object):
    """ 只有一个counter值和结束标识的线程类 """
    def __init__(self):
        """ 将counter设置为0， 运行标识设置为True """
        self.val = 0
        self.running = True
    
    def increment(self):
        """ counter递增1 """
        self.val +=1

    def sendVal(self, msg):
        """ 将当前counter值发给询问的线程 """
        req = msg[0]
        req.send((cg.self(), self.val))

    def setStop(self):
        """ 将运行标志设成False """
        self.running = False

    def run(self):
        """ 线程的入口点 """
        #Register the handle functions for various messages:
        r = cg.Receiver()
        r.addHandler('increment', self.increment)
        r.addHandler((cg.Process, 'value'), self.sendVal, cg.Message)
        r.addHandler('stop', self.setStop)
        #断续处理新消息，直到被要求结束
        while self.running:
            r.receive()

#为了启动一个线程，要这样做
counter = cg.spawn(ExampleThread().run)
#为了处理counter线程的回应，需要一个Receiver对象，并且正确注册：
response = cg.Receiver()
response.addHandler((counter, int), lambda msg: msg[1], cg.Message)

#示例
counter.send('increment')
counter.send('increment')
#请求线程的当前值，并打印线程的回应
counter.send((cg.self(), 'value'))
print response.receive()
#告诉线程再递增一次
counter.send('increment')
#再次请求线程的当前值，并打印线程的回应
counter.send((cg.self(), 'value'))
print response.receive()
#告诉线程停止运行
counter.send('stop')

'''
9.7 储存线程信息
'''
#你想给每个线程分配一些空间来存储只有它自己能访问的信息
#比起Python提供的广泛使用的threading模块，利用thread模块支持编写的更底层代码的通用型略好一点
_tss = { }
try:
    import thread
except ImportError:
    # 我们运行在一个单线程平台上，至少，Python解释器并未被编译成支持多线程
    # 所以对每个调用我们都返回同样的字典——毕竟只有一个线程
    def get_thread_storage():
        return _tss
else:
    #我们有线程，所以开始干活
    _tss_lock = thread.allocate_lock()
    def get_thread_storage():
        """ 返回一个线程特有的存储字典 """
        thread_id = thread.get_ident()
        _tss_lock.acquire()
        try:
            return _tss.set_default(thread_id, { })
        finally:
            _tss_lock.release()
#Python2.4提供了更简单更快的实现，这要归功于新的threading.local函数
try:
    import threading
except ImportError:
    import dummy_threading as threading
_tss = threading.local()
def get_thread_storage():
    return _tss.__dict__

print get_thread_storage()