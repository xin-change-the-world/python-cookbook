#!/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
# python cookbook 第十九章 迭代器和生成器 660
# Writer：xin.change.the.world@gmail.com
# Date：2014-07-08
# github: https://github.com/xin-change-the-world/python-cookbook
#
'''
'''
引言 660
19.1　编写一个类似range的浮点数递增的函数 663
19.2　从任意可迭代对象创建列表 665
19.3　生成Fibonacci序列 667
19.4　在多重赋值中拆解部分项 669
19.5　自动拆解出需要的数目的项 670
19.6　以步长n将一个可迭代对象切成n片 672
19.7　通过重叠窗口循环序列 674
19.8　并行地循环多个可迭代对象 678
19.9　循环多个可迭代对象的矢量积 680
19.10　逐段读取文本文件 683
19.11　读取带有延续符的行 685
19.12　将一个数据块流处理成行流 687
19.13　用生成器从数据库中抓取大记录集 688
19.14　合并有序序列 690
19.15　生成排列、组合以及选择 694
19.16　生成整数的划分 696
19.17　复制迭代器 697
19.18　迭代器的前瞻 701
19.19　简化队列消费者线程 703
19.20　在另一个线程中运行迭代器 705
19.21　用itertools.groupby来计算汇总报告 706
'''
'''
19.1 编写一个类似range的浮点数递增的函数（只对整数有效）
'''
import itertools
def frange(start, end=None, inc=1.0):
    ''' 一个类似xrange的生成器，生成浮点值 '''
    # 模拟range/xrange的参数的含义
    if end is None:
        end = start + 0.0    # 确保end是浮点数
        start = 0.0
    assert inc
    for i in itertools.count():
        next = start + i * inc
        if (inc>0.0 and next>=end) or (inc<0.0 and next<=end):
            break
        yield next

# 不管任何时候，如果需要更快的速度，考虑使用itertools
import math
def frange1(start, end=None, inc=1.0):
    if end == None:
        end = start + 0.0
        start = 0.0
    nitems = int(math.ceil((end-start)/inc))
    for i in xrange(nitems):
        yield start + i * inc
'''
import math, Numeric
def frange2(start, end=None, inc=1.0, typecode=None):
    if end == None:
        end = start + 0.0
        start = 0.0
    nitems = math.ceil((end-start)/inc)
    return Numeric.arange(nitems) * inc + start
'''
'''
19.2 从任意可迭代对象创建列表
'''
# 你有个可迭代对象x（它可能是一个序列或者任何可以迭代的类型，如一个可迭代对象、
# 一个file或一个dict），但需要的是一个list对象y，y和x以相同的顺序拥有相同的元素
# 如果你确定可迭代对象x是有界的（例如循环for item in x能够自动终止），则可以不费吹灰之力地获得对应的列表对象：
# y = list(x)
# 然而，如果你确定x是无界的，或者你不确定它是否有界，那么必须确保在调用list前终止x，
# 具体地说，如果你想用x中的不超过N个元素来创建一个列表，则标准库模块itertools的函数islice正是你所需要的工具：
# import itertools
# y = list(itertools.islice(x, N))

'''
19.3 生成Fibonacci序列
'''
# 需要一个无界的生成器，它能一次一项地生成Fibonacci数的整个序列（无限的）。
def fib():
    x, y = 0, 1
    while True:
        yield x
        x, y = y, x + y
import itertools
print list(itertools.islice(fib(), 10))