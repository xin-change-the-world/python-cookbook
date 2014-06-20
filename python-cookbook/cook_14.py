#!/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第十四章 Web编程 502
# Writer：xin.change.the.world@gmail.com
# Date：2014-06-12
# github: https://github.com/xin-change-the-world/python-cookbook
#
'''
'''
引言 502
14.1　测试CGI是否在工作 503
14.2　用CGI脚本处理URL 506
14.3　用CGI上传文件 507
14.4　检查web页面的存在 509
14.5　通过HTTP检查内容类型 510
14.6　续传HTTP下载文件 512
14.7　抓取Web页面时处理Cookie 513
14.8　通过带身份验证的代理进行HTTPS导航 516
14.9　用Jython实现Servlet 517
14.10　寻找Internet Explorer的cookie 519
14.11　生成OPML文件 521
14.12　聚合RSS Feed 524
14.13　通过模板将数据放入Web页面 527
14.14　在Nevow中呈现任意对象 530
'''
'''
14.1　测试CGI是否在工作
'''
'''
apache httpd.conf 配置
ScriptAlias /cgi-bin/ "D:/xampp/cgi-bin/"

<Directory "D:/xampp/cgi-bin/">
    AllowOverride None
    Options None
    Order allow,deny
    Allow from all
    Options ExecCGI
</Directory>

AddHandler cgi-script .cgi .py
ScriptInterpreterSource Registry
'''
print "Content-type: text/html"
print
print "<html><head><title>Situation snapshot</title></head><body><pre>"
import sys
sys.stderr = sys.stdout
import os
# Python 内置的 cgi.escape 可以转义编码 HTML 特殊字符
from cgi import escape
print "<strong>Python %s</strong>" % sys.version
keys = os.environ.keys()
keys.sort()
for k in keys:
    print "%s\t%s" % (escape(k), escape(os.environ[k]))
print "</pre></body></html>"

'''
14.2　用CGI脚本处理URL 506
14.3　用CGI上传文件 507
'''

'''
14.4　检查web页面的存在 509
'''
"""
httpExists.py
一个快速检查web文件存在性的方法
用法：
>>> import httpExists
>>> httpExists.httpExists('http://www.python.org/')
True
>>> httpExists.httpExists('http://www.python.org/ddddddddddd')
Sstatus 404 Not Found : http://www.python.org/ddddddddddd
False
"""
'''
import httplib, urlparse
def httpExists(url):
    host, path = urlparse.urlsplit(url)[1:3]
    if ':' in host:
        # 指定了端口试图使用它
        host, port = host.split(':',1)
        try:
            port = int(port)
        except ValueError:
            print 'invalid port number %r' % (port,)
    else:
        # 未指定端口，使用默认的
        port = None
    try:
        connection = httplib.HTTPConnection(host, port = port)
        connection.request("HEAD", path)
        resp = connection.getresponse()
        if resp.status == 200:     # 正常的“找到了”状态
            found = True
        elif resp.status == 302:   # 对临时重定向递归
            found = httpExists(urlparse.urljoin(url, resp.getheader('location', '')))
        else: #其他的未找到
            print "Status %d %s : %s" % (resp.status, resp.reason, url)
            found = False

def _test():
    import doctest, httpExists
    return doctest.testmod(httpExists)

_test()
'''
'''
14.5 通过HTTP检查内容类型
'''
import urllib
def isContentType(URLorFile, contentType='text'):
    """
    # 判断URL（urllib.urlopen访问的伪文件对象）是否是要求的类型（默认为文本）
    """
    try:
        if isinstance(URLorFile, str):
            thefile = urllib.urlopen(URLorFile)
        else:
            thefile = URLorFile
        result = thefile.info.getmaintype() == contentType.lower()
        if thefile is not URLorFile:
            thefile.close()
    except IOError:
        result = False
    return result

'''
14.6 续传HTTP下载文件
'''
import urllib, os
class myURLOpener(urllib.FancyURLopener):
    """ 子类化以允许err 206（部分文件被传送），对我们而言这不是错误 """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass
def getrest(dlFile, fromUrl, verbose=0):
    myUrlclass = myURLOpener()
    if os.path.exists(dlFile):
        outputFile = open(dlFile, "ab")
        existSize = os.path.getsize(dlFile)
        # 如果文件存在，下载剩余部分
        myUrlclass.addheader("Range","bytes=%s-" % (existSize))
    else:
        outputFile = open(dlFile, "wb")
        existSize = 0
    webPage = myUrlclass.open(fromUrl)
    if verbose:
        for k, v in webPage.headers.items():
            print k, "=", v
    # 如果我们已经有了整个文件，没必要再下载以便
    numBytes = 0
    webSize = int(webPage.headers['Content-Length'])
    if webSize == existSize:
        if verbose:
            print "File (%s) was already downloaded from URL(%s)" % (dlFile, fromUrl)
    else:
        if verbose:
            print "Downloading %d more bytes" % (webSize-existSize)
        while True:
            data = webPage.read(8192)
            if not data:
                break
            outputFile.write(data)
            numBytes = numBytes + len(data)
    webPage.close()
    outputFile.close()
    if verbose:
        print "downloaded", numBytes, "bytes from ", webPage.url
    return numBytes

'''
14.7 抓取Web页面时处理Cookie
'''
# 需要抓取一些要求你处理cookie（比如，保存你接收到的cookie，如果已经接受过cookie，就载入并发送cookie给web站点）的web页面（或web中的其他资源）
import os.path, urllib2
from urllib2 import urlopen, Request
COOKIEFILE = 'cookies.lwp'    # 用于保存和读取的“cookiejar”文件
# 首先尝试最好的方案cookielib
try:
    import cookielib
except ImportError:           # 无cookielib，尝试ClientCookie
    cookielib = None
    try:
        import ClientCookie
    except ImportError:
        cj = None
    else:
        urlopen = ClinetCookie.urlopen
        cj = ClientCookie.LWPCookieJar()
        Request = ClientCookie.Request
else:
    cj = cookielib.LWPCookieJar()
# 如果有的话，载入cookie，然后创建并安装一个opener来使用cookie
if cj is not None:
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE)
    if cookielib:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    else:
        opener = ClinetCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
        ClinetCookie.install_opener(opener)
# 比如，尝试连接一个设置了cookie的URL
theurl = 'http://www.diy.co.uk'
txdata = None # 或，如果是POST 而不是 GET， 则txdata=urllib.urlencode(somedict)
txheaders = {'User-agent':'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
try:
    req = Request(theurl, txdata, txheaders) # 创建一个request对象
    handle = urlopen(req)
except IOError, e:
    print 'Failed to open "%s".' % theurl
    if hasattr(e, 'code'):
        print 'Error code: %s.' % e.code
else:
    print 'Here are the headers of the page:'
    print handle.info
# 也可以使用handle.read()获得页面，用handle.geturl()获得真正的URL（如果有重定向，可能和theurl不同）
if cj is None:
    print "Sorry, no cookie jar, can't show you any cookies today"
else:
    print 'Here are the cookies received so far:'
    for index, cookie in enumerate(cj):
        print index, ':', cookie
    cj.save(COOKIEFILE)    # save the cookies again

'''
14.8 通过带身份验证的代理进行HTTPS导航
'''
'''
14.9 用Jython实现Servlet
'''
'''
14.10 寻找Internet Explorer的cookie
'''
'''
14.11 生成OPML文件
'''
'''
14.12 聚合RSS Feed
'''
'''
14.13 通过模板将数据放入Web页面
'''
# Nevow web开发包同Twisted网络架构协作，为基于Twisted异步模式的web站点提供了强大的模板能力
from twisted.application import service, internet
from nevow import rend, loaders, appserver
dct = [{'name':'Mark'}]
class Pg(rend.Page):
	docFactory = loaders.htmlstr("""
		<html><head><title>Name</title></head>
		    <body>
		        <ul nevow:data="dct" nevow:render="sequence">
                    <li nevow:pattern="item" nevow:render="mapping">
                    	<span><nevow:slot name="name">&nbsp;</span>
                    </li>
		        </ul>
		        <H1></H1>
		    </body>
		</html>
		""")
	def __init__(self, dct):
		self.data_dct = dct
		rend.Page.__init__(self)
site = appserver.NevowSite(Pg(dct))
application = service.Application("example")
ilnternet.TCPServer(8080, site).setServiceParent(application)

'''
14.14 在Nevow中呈现任意对象
'''