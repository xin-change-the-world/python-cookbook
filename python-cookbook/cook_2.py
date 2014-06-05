#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第二章 文件
# Auther：张广欣
# Date：2014-06-04
#
#
'''
###############################
'''
2.0 引言
'''
input = open('data', 'r')
output = open('/tmp/spam', 'w')
#open接受由斜线字符（/）分隔开的目录和文件名构成的文件路径，而不管操作系统本身的倾向
'''
2.1 读取文件
'''
#最方便的方法是一次性读取文件中的所有内容并放置到一个大字符串中
all_the_text = open('thefile.txt').read()#文本文件中的所有文本
all_the_data = open('abinfile','rb').read()#二进制文件中的所有数据
#为安全起见，最好给打开的文件对象指定一个名字，这样在完成操作后，可以迅速关闭文件，
#防止一些无用的文件对象占用内存
file_object = open('thefile.txt')
try:
    all_the_text = file_object.read()
finally:
    file_object.close()
#注意不要把open也放到try里面去，因为如果open的时候出错了，那么就没有什么东西绑定到
#file_object对象上，在finally里，也就没有file_object需要关闭
#不一定非要用try/finally，但是用了效果更好，因为它可以保证文件对象被关闭，即使在读取中发生了严重错误
'''
#最简单、最快，也最具Python风格的方法是逐行读取文本文件内容，并将读取的数据放置到一个字符串列表中：
list_of_all_the_lines = file_object.readlines()
#这样读出的每行文本末尾都带有“\n”符号，如果不想这样，还可以这样写：
list_of_all_the_lines = file_object.read().splitlines()
list_of_all_the_lines = file_object.read().split('\n')
list_of_all_the_lines = [L.rstrip('\n') for L in file_object]
'''
#最简单最快的逐行处理文本文件的方法是，用一个简单的for循环语句:
'''
for line in file_object:
    process line
#这样会在每行末尾留下“\n”，可以这样：
for line in file_object:
    line = line.rstrip('\n')
    process line
#或者你想去除每行末尾的空白符（不只是“\n”）
line = line.rstrip()
'''
#如果不确定文本文件会用什么样的换行符，可以讲open的第二个参数设定为'rU'指定通用换行符转化
#无论什么平台，各种换行符都被映射成'\n'

