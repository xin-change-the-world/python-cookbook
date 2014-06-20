#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第十三章 网络编程
# Writer：张广欣
# Date：2014-06-19
#
#
'''
"""
引言 462
13.1　通过Socket数据报传输消息 464
13.2　从Web抓取文档 466
13.3　过滤FTP站点列表 467
13.4　通过SNTP协议从服务器获取时间 468
13.5　发送HTML邮件 469
13.6　在MIME消息中绑入文件 471
13.7　拆解一个分段MIME消息 474
13.8　删除邮件消息中的附件 475
13.9　修复Python 2.4的email.FeedParser 解析的消息 477
13.10　交互式地检查POP3邮箱 479
13.11　探测不活动的计算机 482
13.12　用HTTP监视网络 487
13.13　网络端口的转发和重定向 489
13.14　通过代理建立SSL隧道 492
13.15　实现动态IP协议 495
13.16　登录到IRC并将消息记录到磁盘 498
13.17　访问LDAP服务 500
"""
'''
前言
'''
# wget.py
import sys, urllib
def reporthook(*a): print a
for url in sys.argv[1:]:
    i = url.rfind('/')
    file = url[i+1:]
    print url, "->", file
    urllib.urlretrieve(url, file, reporthook)
# 给这个脚本传入一个或多个URL作为命令行参数，这个脚本会获取URL中的数据并存入本地文件，
# 文件名和URL的最后一个部分的名字相同。
'''
13.1 通过Socket数据报传输消息 464
'''
# 在网络中的计算机能够以一种轻量级的风格通过小消息通信，同时也不要求绝对的可靠性
# server.py
import socket
port = 8081
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 从给定的端口，从任何发送者，接收UDP数据报
s.bind(("", port))
print "waiting on port:", port
while True:
    # 接收一个数据报（最大到1024个字节）
    data, addr = s.recvfrom(1024)
    print "Received:", data, "from", addr
# client.py
import socket
port = 8081
host = "localhost"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("Hi, xin! It's working.", (host, port))
# 用socket数据报来发送短文本消息的功能很容易实现，也是一种轻量级的消息传递机制。
# 但在数据的可靠性必须得到保证的时候，socket数据报就不适用了。
# 不要使用本节的简单代码来发送巨大的数据报消息，尤其是Windows下
# Windows可能并不遵从缓存限制。为了发送大消息，你可能得像下面这么做
BUFSIZE = 1024
while msg:
    bytes_sent = s.sendto(msg[:BUFSIZE], (host, port))
    msg = msg[bytes_sent]
# sendto方法返回的是它实际发送的字节数，所以，如果你每次发送的数据报都不大于BUFSIZE,
# 则每次你都需要从上次结束的地方继续传送。

'''
13.2 从Web抓取文档
'''
from urllib import urlopen
doc = urlopen("http://www.python.org")
print doc.read() # 全部文本
print doc.info() # 文档头部
print doc.info().getheader('Content-Type') # 返回“text/html”

'''
13.3 过滤FTP站点列表
'''
# 你的站点列表中有一些FTP站点可能总是关闭或宕机，对列表进行过滤，获得所有能访问的站点的列表。
import socket, ftplib
def isFTPSiteUp(site):
    try:
        ftplib.FTP(site).quit()
    except socket.error:
        return False
    else:
        return True
def filterFTPsites(sites):
    return [site for site in sites if isFTPSiteUp(site)]
# 或者使用filter(isFTPSiteUp, sites)也可以返回同样的列表

'''
13.4 通过SNTP协议从服务器获取时间
'''
# 联络一个SNTP（simplified Network Time Protocol，简单网络时间协议）服务器（遵循RFC 2030）来获取当天的时间
import socket, struct, sys, time 
TIME1970 = 2208988800L  # Thanks to F.Lundh
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = '\x1b' + 47 * '\0'
client.sendto(data, (sys.argv[1], 123))
data, address = client.recvfrom(1024)
if data:
    print 'Response Received from:', address
    t = struct.unpack('!12I', data)[10]
    t -= TIME1970
    print '\tTime=%s' % time.ctime(t)

'''
13.5 发送HTML邮件
'''
def createhtmlmail(subject, html, text=None):
    # 创建MIME消息，最终呈现为HTML或文本
    import MimeWriter, mimetools, cStringIO
    if text is None:
        # 创建HTML字符串呈现的纯文本内容
        # 除非通过参数制定了更好的纯文本版本
        import htmllib, formatter
        textout = cStringIO.StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(textout))
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()
        text = textout.getvalue()
        del textout, formtext, parser
    out = cStringIO.StringIO()           # 消息的输出缓存
    htmlin = cStringIO.StringIO(html)    # HTML的输入缓存
    txtin = cStringIO.StringIO(text)           # 纯文本的输入缓存
    writer = MimeWriter.MimeWriter(out)
    # 设置一些基本的头部，在此放入标题，根据RFC的规定
    # smtplib.sendmail会在消息中找标题
    writer.addheader("subject", subject)
    writer.addheader("MIME-Version", "1.0")
    # 消息的多头部分，在某些邮件客户端中Multipart/alternatives
    # 比multipart/mixed 工作得更好
    writer.startmultipartbody("alternative")
    writer.flushheaders()
    # 纯文本段：直接复制，假设为iso-8859-1
    subpart = writer.nextpart()
    pout = subpart.startbody("text/plain",[("charset", 'iso-8859-1')])
    pout.write(txtin.read())
    txtin.close()
    # 消息的HTML部分：设为quoted-printable，以防万一
    subpart = writer.nextpart()
    subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
    pout = subpart.startbody("text/html", [("charset", 'us-ascii')])
    mimetools.encode(htmlin, pout, 'quoted-printable')
    htmlin.close()
    # 完工；关闭writer并将消息作为字符串返回
    writer.lastpart()
    msg = out.getvalue()
    out.close()
    return msg
#示例
import smtplib
f = open("newsletter.html", 'r')
html = f.read()
f.close()
try:
    f = open("newsletter.txt", 'r')
    text = f.read()
except IOError:
    text = None
subject = "Today's Newsletter!"
message = createhtmlmail(subject, html, text)
server = smtplib.SMTP("localhost")
server.sendmail('xin.change.the.world@gmail.com', 'xin.change.the.world@gmail.com', message)
server.quit()

'''
13.6 在MIME消息中绑入文件
'''
'''
13.7 拆解一个分段MIME消息
'''
'''
13.8 删除邮件消息中的附件
'''
'''
13.9 修复Python2.4的email.FeedParser解析的消息
'''
'''
13.10 交互式地检查POP3邮箱
'''
'''
13.11 探测不活动的计算机
'''
# 需要监视一些链接到TCP/IP网络的计算机的工作状态。
# 本节的思路是每台计算机都周期性地发送一个代表着心跳的UDP包到某一个扮演服务器角色的计算机
# 服务器会跟踪每台计算机在上次发送心跳之后经历的时间并报告那些沉默时间太长的计算机
# 下面试一个“客户端”程序，HeartbeatClient.py，它运行在我们需要检测的计算机上：
""" Heartbeat客户端，周期性发送UDP包 """
import socket, time
SERVER_IP = '192.168.0.15'; SERVER_PORT = 43278; BEAT_PERIOD = 5
print 'Sending heartbeat to IP %s, port %d' % (SERVER_IP, SERVER_PORT)
print 'press Ctrl-C to stop'
while True:
    hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hbSocket.sendto('PyHB', (SERVER_IP, SERVER_PORT))
    if __debug__:
        print 'Time: %s' % time.ctime()
    time.sleep(BEAT_PERIOD)

# 而服务器程序会接收并跟踪所有的“心跳”，它运行的计算机的地址必须和“客户端”程序中的SERVER_IP一致。
# 服务器必须支持并发，这是因为来自不同计算机的心跳可能会同时到达。一个服务器程序有两种方法来支持并发：
# 多线程或异步操作。下面试一个多线程的ThreadedBeatServer.py，只使用了Python标准库中的模块
""" 多线程heartbeat服务端 """
import socket, threading, time
UDP_PORT = 43278; CHECK_PERIOD = 20; CHECK_TIMEOUT = 15
class Heartbeats(dict):
    """ 用线程锁管理共享的heartbeats字典 """
    def __init__(self):
        super(Heartbeats, self).__init__()
        self._lock = threading.Lock()
    def __setitem__(self, key, value):
        """ 为某客户端创建或更新字典中的条目 """
        self._lock.acquire()
        try:
            super(Heartbeats, self).__setitem__(key, value)
        finally:
            self._lock.release()
    def getSilent(self):
        """ 返回沉默期长于CHECK_TIMEOUT的客户端的列表 """
        limit = time.time() - CHECK_TIMEOUT
        self._lock.acquire()
        try:
            silent = [ip for (ip, ipTime) in self.items() if ipTime < limit]
        finally:
            self._lock.release()
        return silent

class Receiver(threading.Thread):
    """ 接受UDP包并将其记录在heartbeats字典中 """
    def __init__(self, goOnEvent, heartbeats):
        super(Receiver, self).__init__()
        self.goOnEvent = goOnEvent
        self.heartbeats = heartbeats
        self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recSocket.settimeout(CHECK_TIMEOUT)
        self.recSocket.bind(('', UDP_PORT))
    def run(self):
        while self.goOnEvent.isSet():
            try:
                data, addr = self.recSocket.recvfrom(5)
                if data == 'PyHB':
                    self.heartbeats[addr[0]] = time.time()
            except socket.timeout:
                pass
def main(num_receivers=3):
    receiverEvent = threading.Event()
    receiverEvent.set()
    heartbeats = Heartbeats()
    receivers = []
    for i in range(num_receivers):
        receiver = Receiver(goOnEvent=receiverEvent, Heartbeats=heartbeats)
        receiver.start()
        receivers.append(receiver)
    print 'Threaded heartbeat server listening on port %d' % UDP_PORT
    print 'press Ctrl-C to stop'
    try:
        while True:
            silent = heartbeats.getSilent()
            print 'Silent client: %s' % silent
            time.sleep(CHECK_PERIOD)
    except KeyboardInterrupt:
        print 'Exiting, please wait...'
        receiverEvent.clear()
        for receiver in receivers:
            receiver.join()
        print 'Finished.'
main()

# 作为一种备选方案，下面给出异步AsyncBeatServer.py程序，这个程序借助了强大的Twisted的力量：
import time
from twisted.application import internet, service
from twisted.internet import protocol 
from twisted.python import log
UDP_PORT = 43278; CHECK_PERIOD = 20; CHECK_TIMEOUT = 15
class Receiver(protocol.DatagramProtocol):
	""" 接收UDP包并将其记录在“客户端”的字典中 """
	def datagramReceived(self, data, (ip, port)):
		if data == 'PyHB':
			self.callback(ip)
class DetectorService(internet.TimerService):
	""" 探测长时间没有心跳的客户端 """
	def __init__(self):
		internet.TimerService.__init__(self, CHECK_PERIOD, self.detect)
		self.beats = {}
	def update(self, ip):
		self.beats[ip] = time.time()
	def detect(self):
		""" 记录沉默期长于CHECK_TIMEOUT的客户端的列表 """
		limit = time.time() - CHECK_TIMEOUT
		silent = [ip for (ip, ipTime) in self.beats.items() if ipTime < limit]
		log.msg('Silent clients: %s' % silent)
application = service.Application('Heartbeat')
# define and link the silent clients' detector service
# 定义并连接detector服务
detectorSvc = DetectorService()
detectorSvc.setServiceParent(application)
# 创建一个Receiver协议的实例，给它设置回调函数
receiver = Receiver()
receiver.callback = detectorSvc.update
# 定义并连接UDP服务， 传入receiver
udpServer = internet.UDPServer(UDP_PORT, receiver)
udpServer.setServiceParent(application)
# 在Twisted运行时所有服务自动开始
log.msg('Asynchronous heartbeat server listening on port %d\n'
	'press Ctrl-c to stop\n' % UDP_PORT)

'''
13.12 用HTTP监视网络
'''
# 你想实现某种特殊的HTTP服务，以便于监视你的网络
# Python标准库模块BaseHTTPServer使得这个特殊的HTTP服务的实现变得很容易
# 下面给出一个HTTP服务程序例子，它可以在服务主机上运行本地命令来获得数据并回应每个GET请求
import BaseHTTPServer, shutil, os
from cStringIO import StringIO
class MyHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # 我们服务的HTTP路径以及我们服务的命令行命令
    cmds = {'/ping': 'ping www.baidu.com',
            '/netstat': 'netstat -a',
            '/tracert': 'tracert www.baidu.com',
            '/srvstats': 'net statistics server',
            '/wsstats': 'net statistics workstation',
            '/route': 'route print',
            }
    def do_GET(self):
        """ 服务一个GET 请求 """
        f = self.send_head()
        if f:
            f = StringIO()
            machine = os.popen('hostname').readlines()[0]
            if self.path == '/':
                heading = "Select a command to run on %s" % (machine)
                body = (self.getMenu() + 
                        "<p>The screen won't update until the selected"
                        "command has finished. Please be patient.")
            else:
                heading = "Execution of ''%s'' on %s" % (self.cmds[self.path], machine)
                cmd = self.cmds[self.path]
                body = '<a href="/">Main Menu&lt;/a&gt;<pre>%s</pre>\n' % os.popen(cmd).read()
                # 翻译CP437 -> Latin 1，对于瑞典语的Windows是需要的
                body = body.decode('cp437').encode('latin1')
            f.write("<html><head><title>%s</title></head>\n" % heading)
            f.write('<body><H1>%s</H1>\n' % (heading))
            f.write(body)
            f.write('</body></html>\n')
            f.seek(0)
            self.copyfile(f, self.wfile)
            f.close()
        return f

    def do_HEAD(self):
        """" 服务一个HEAD请求 """
        f = self.send_head()
        if f:
            f.close()
    def send_head(self):
        path = self.path
        if not path in ['/'] + self.cmds.keys():
            head = 'Command "%s" not found. Try one of these:<ul>' % path
            msg = head + self.getMenu()
            self.send_error(404, msg)
            return None
        self.send_response(200)
        self.send_header("Content-Type", 'text/html')
        self.end_headers()
        f = StringIO()
        f.write("A test %s\n" % self.path)
        f.seek(0)
        return f
    def getMenu(self):
        keys = self.cmds.keys()
        keys.sort()
        msg = []
        for k in keys:
            msg.append('<li><a href="%s">%s => %s&lt;/a&gt;</li>' % (k, k, self.cmds[k]))
        msg.append('</ul>')
        return "\n".join(msg)
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

def main(HandlerClass = MyHTTPRequestHandler, ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)
main()

'''
13.13 网络端口的转发和重定向
'''
# 需要将某个网络端口转发到另一个主机，但可能会是不同的端口
# 使用threading和socket模块的类就能完成我们需要的端口转发和重定向
import sys, socket, time, threading
LOGGING = True
loglock = threading.Lock()
def log(s, *a):
    if LOGGING:
        loglock.acquire()
        try:
            print '%s:%s' % (time.ctime(), (s % a))
            sys.stdout.flush()
        finally:
            loglock.release()
class PipeThread(threading.Thread):
    pipes = []
    pipeslock = threading.Lock()
    def __init__(self, source, sink):
        Thread.__init__(self)
        self.source = source
        self.sink = sink
        log('Creating new pipe thread %s ( %s -> %s )',
            self, source.getpeername(), sink.getpeername())
        self.pipeslock.acquire()
        try: self.pipes.append(self)
        finally: self.pipeslock.release()
        log('%s pipes now active', pipes_now)
    def run(self):
        while True:
            try:
                data = self.source.recv(1024)
                if not data: break
                self.sink.send(data)
            except:
                break
        log('%s terminating', self)
        self.pipeslock.acquire()
        try: pipes_left = len(self.pipes)
        finally: self.pipeslock.release()
        log('%s pipes still active', pipes_left)
class Pinhole(threading.Thread):
    def __init__(self, port, newhost, newport):
        Thread.__init__(self)
        log('Redirecting:localhost:%s->%s:%s', port, newhost, newport)
        self.newhost = newhost
        self.newport = newport
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(5)
    def run(self):
        while True:
            newsock, address = self.sock.accept()
            log('Creating new session for %s:%s', *address)
            fwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fwd.connect((self.newhost, self.newport))
            PipeThread(newsock, fwd).start()
            PipeThread(fwd, newsock).start()
'''
if __name__=='__main__':
    print 'Starting Pinhole port forwarder/redirector'
    import sys
    # 获得参数，如果出错给出帮助
    try:
        port = int(sys.argv[1])
        newhost = sys.argv[2]
        try: newport = int(sys.argv[3])
        except IndexError: newport = port
    except (ValueError, IndexError):
        print 'Usage: %s port newhost [newport] ' % sys.argv[0]
        sys.exit(1)
    # 开始操作
    sys.stdout = open('pinhole.log', 'w')
    Pinhole(port, newhost, newport).start()
'''