#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第八章 调试和测试
# Writer：张广欣
# Date：2014-06-18
#
#
'''
"""
8.1　阻止某些条件和循环的执行 316
8.2　在Linux上测量内存使用 317
8.3　调试垃圾回收进程 318
8.4　捕获和记录异常 320
8.5　在调试模式中跟踪表达式和注释 322
8.6　从traceback中获得更多信息 324
8.7　当未捕获异常发生时自动启用调试器 327
8.8　简单的使用单元测试 328
8.9　自动运行单元测试 330
8.10　在Python 2.4中使用doctest和unittest 331
8.11　在单元测试中检查区间 334
"""
'''
8.1 阻止某些条件和循环的执行
'''
# 只读的全局变量__debug__。如果Python运行时没有-O（optimize）命令行参数选项，__debug__的值是True
# 如果带有该选项，__debug__的值是False。
# 而且Python编译器知道__debug__的存在，当Python运行时带有优化选项，编译器会移除所有被 if __debug__
# 保护的代码块，这样可以节省更多内存，并提升执行速度
'''
8.2 在Linux上测量内存使用
'''
# 你很像监控运行在Linux上的程序究竟占用了多少内存，然后标准库模块resourdce并不能在Linux中正确的工作
# 我们可以基于Linux的/proc伪文件系统编写我们的测量程序
import os
_proc_status = '/proc/%d/status' % os.getpid()
_scale = {'KB':1024.0, 'mB': 1024.0*1024.0,
          'KB':1024.0, 'MB': 1024.0*1024.0}
def _VmB(VmKey):
    ''' 给定VmKey字符串，返回字节数 '''
    # 获得伪文件/proc/<pid>/status
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except IOError:
        return 0.0 # non-Linux?
    #获得VmKey行，入‘VmRSS:  999  KB\n ...’
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # 依照空白符切割
    if len(v) < 3:
        return 0.0  # 无效格式？

    # 将Vm值转成字节
    return float(v[1]) * _scale[v[2]]
def memory(since=0.0):
    ''' 返回虚拟内存使用的字节数 '''
    return _VmB('VmSize:') - since
def resident(since=0.0):
    ''' 返回常驻内存使用的字节数 '''
    return __VmB('VmRSS:') - since
def stacksize(since=0.0):
    ''' 返回栈使用的字节数 '''
    return _VmB('VmStk:') - since

'''
8.3 调试垃圾回收进程
'''
# 你已经知道你的程序中有内存泄露现象，但你并不清楚究竟是什么东西造成的
# 因此你需要获得更多的信息来帮助你定位泄露发生的地点
import gc
def dump_garbage():
    """ 展示垃圾都是什么东西 """
    # 强制收集
    print "\nGARBAGE OBJECTS:"
    for x in gc.garbage:
        s = str(x)
        if len(s) > 80: s = s[:77] + '...'
        print type(x), "\n ", s
gc.enable()
gc.set_debug(gc.DEBUG_LEAK)
# 模拟一个泄露（一个引用自身的列表）并展示
l = [ ]
l.append(l)
del l
dump_garbage()

'''
8.4 捕获和记录异常
'''
# 你需要捕获异常并记录他们的回溯和错误信息，然后再继续执行程序。
# 一个典型的情况是程序需要一个接一个处理许多独立的文件。
# 其中一些的格式可能是问题的，因而会引发异常。你需要捕获异常，并记录错误信息，然后继续你的文件处理流程
import cStringIO, traceback
def process_all_files(all_filenames,
	                  fatal_exceptions=(KeyboardInterrupt, MemoryError)):
    bad_filenames = {}
    for one_filename in all_filenames:
    	try:
    		process_one_file(one_filename):
    	except fatal_exceptions:
    		raise
    	except Exception:
    		f = cStringIO.StringIO()
    		traceback.print_exc(file=f)
    		bad_filenames[one_filename] = f.getvalue()
    return bad_filenames

'''
8.5 在调试模式中跟中表达式和注释
'''