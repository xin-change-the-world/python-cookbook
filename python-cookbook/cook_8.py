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
            process_one_file(one_filename)
        except fatal_exceptions:
            raise
        except Exception:
            f = cStringIO.StringIO()
            traceback.print_exc(file=f)
            bad_filenames[one_filename] = f.getvalue()
    return bad_filenames

'''
8.5 在调试模式中跟踪表达式和注释
'''
# 你现在编写的程序无法使用可交互的、单步执行的调试器。因此，你需要详细记录状态和控制分支的信息来进行高效的调试
# traceback模块的extract_stack函数是解决问题的关键
# traceback.extract_stack返回的是4个子项的元组的列表，4个子项分别是文件名、行号、函数名以及调用声明的代码
# 每个元组都代表着栈中的一次调用记录。
import sys, traceback
traceOutput = sys.stdout
watchOutput = sys.stdout
rawOutput = sys.stdout
# 调用watch(secretOfUniverse)打印出如下的信息：
# File "trace.py", line 57, in __testTrace
#    secretOfUniverse <int> = 42
watch_format = ('File "%(fileName)s", line %(lineNumber)d, in'
                ' %(methodName)s\n   %(varName)s <%(varType)s>'
                ' = %(value)s\n\n')
def watch(variableName):
    if __debug__:
        stack = traceback.extract_stack()[-2:][0]
        actualCall = stack[3]
        if actualCall is None:
            actualCall = "watch([unknown])"
        left = actualCall.find('(')
        right = actualCall.rfind(')')
        paramDict = dict(varName=actualCall[left+1:right].strip(),
                         varType=str(type(variableName))[7:-2],
                         value=repr(variableName),
                         methodName=stack[2],
                         lineNumber=stack[1],
                         fileName=stack[0])
        watchOutput.write(watch_format % paramDict)
# 调用trace("this line was executed")打印出如下的信息：
# File "trace.py", line 64, in ?
#     this line was executed
trace_format = ('File "%(fileName)s", line %(lineNumber)d, in'
                ' %(methodName)s\n %(text)s\n\n')
def trace(text):
    if __debug__:
        stack = traceback.extract_stack()[-2:][0]
        paramDict = dict(text=text,
                         methodName=stack[2],
                         lineNumber=stack[1],
                         fileName=stack[0])
        watchOutput.write(trace_format % paramDict)

#调用raw("some raw text")打印出如下的信息：
# some raw text
def raw(text):
    if __debug__:
        rawOutput.write(text)

# 当__debug__是False的时候（当你以-O或-OO开关运行Python解释器的时候）
# 所有与调试相关的代码都会被自动清除
# 示例
def __testTrace():
    secretOfUniverse = 42
    watch(secretOfUniverse)
a = "something else"
watch(a)
__testTrace()
trace("This line was executed!")
raw("Juse some raw text...")

'''
8.6 从traceback中获得更多信息
'''
print "\n============================ 8.6 从traceback中获得更多信息=============================="
# 当一个未捕获的异常发生时，你希望能够打印出所有变量的信息。
# 一个traceback对象，基本上市一个互相关联的节点的列表，每个节点都指向一个帧对象。
# 而帧对象反过来根据traceback的关联节点列表以相反的顺序建立他们自己的链表，所以，
# 我们可以根据需要向前或向右移动。
import sys, traceback
def print_exc_plus():
    """ 打印通常的回溯信息，且附有每帧中的局部变量列表 """
    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    traceback.print_exc()
    print "Locals by frame, innermost last"
    for frame in stack:
        print "Frame %s in %s at line %s" % (frame.f_code.co_name,
                                             frame.f_code.co_filename,
                                             frame.f_lineno)
    for key, value in frame.f_locals.items():
        print "\t%20s = " % key,
        # 我们必须_绝对_避免异常的扩散，而str(value)
        # _能够_引发任何异常，所以我们_必须_捕获所有异常
        try:
            print value
        except:
            print "<ERROR WHILE PRINTING VALUE>"

data = ["1","2",3,"4"] # 手误，我们忘记了给data[2]打上引号
def pad4(seq):
    """
    # 给每个字符串填充0直到总长度为4，注意，完全没必要写这样一个函数；
    # Python已经提供了工具，而且做得很好，这仅仅是一个例子！
    """
    return_value = []
    for thing in seq:
        return_value.append("0" * (4 - len(thing)) + thing)
    return return_value
# 下面我们从traceback.print_exc获得的信息（很有限）：
try:
    pad4(data)
except:
    #traceback.print_exc()
    pass
'''
Traceback (most recent call last):
  File "C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_8.py", line 221, in <module>
    pad4(data)
  File "C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_8.py", line 217, in pad4
    return_value.append("0" * (4 - len(thing)) + thing)
TypeError: object of type 'int' has no len()
'''
# 下面是用本节提供的函数打印出来的信息：
try:
    pad4(data)
except:
    print_exc_plus()

'''
Locals by frame, innermost last
Frame <module> in C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_8.py at line 238
Frame pad4 in C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_8.py at line 218
                   thing =  3
            return_value =  ['0001', '0002']
                     seq =  ['1', '2', 3, '4']
g[Finished in 0.4s]c: collectable <list 00000000027067C8>
Traceback (most recent call last):
  File "C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_8.py", line 236, in <module>
    pad4(data)
  File "C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_8.py", line 218, in pad4
    return_value.append("0" * (4 - len(thing)) + thing)
TypeError: object of type 'int' has no len()
'''

'''
8.7 当未捕获异常发生时自动启用调试器
'''
# 当脚本激发了异常时，Python在通常情况下会打印回溯信息以及终止脚本运行
# 但你却希望当这种情况发生时，Python能够自动启动一个交互式的调试器，如果条件允许的话。
# 通过设置sys.excepthook，可以控制当未捕获异常发生时Python的行为方式
# 此代码片段需要被置入你的sitecustomeize.py
def info(type, value, tb):
    if hasattr(sys, 'psl') or not (
        sys.stderr.isatty() and sys.stdin.isatty()
        ) or issubclass(type, SyntaxError):
        # 交互模式，没有类似TTY的设备或语法错误：什么也不做
        # 只能调用默认的hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback, pdb
        # 非交互模式：因此打印异常
        traceback.print_exception(type, value, tb)
        print 
        # 在事后分析阶段开启调试器
        pdb.pm()
    sys.excepthook = info

# 本节代码需要被放入到sitecustomeize.py中，Python在启动时会自动导入这个文件。
# 当且仅当Python运行在非交互模式以及交互式调试器需要的类TTY设备可用时，函数info才会启动调试器
# 因此，对于CGI脚本、守护进程等，调试器不会被启动。
# 如果你没有sitecustomeize.py文件，可以在你的Python库目录的site-packages子目录中创建一个。

'''
8.8 简单的使用单元测试
'''
# 你发现对标准库模块unittest中的测试器的使用还未简化到极致，你想改进对单元测试的使用以确保那是一件非常简单清楚的事，从而让自己养成勤于测试的习惯
# 将下列的代码存为模块microtest.py，放入Python的sys.path中
import types, sys, traceback
class TestException(Exception): pass
def test(modulename, verbose=None, log=sys.stdout):
    """
    # 执行命名模块中的所有名字中含有__test__的，不接受参数的函数
    # modulename：需要被测试的模块的名字
    # verbose：如果为真，执行时打印测试名
    # 成功时返回None，否则抛出异常
    """
    module = __import__(modulename)
    total_tested = 0
    total_failed = 0
    for name in dir(module):
        if '__test__' in name:
            obj = getattr(module, name)
            if (isinstance(obj, types,FunctionType) and not obj.func_code.co_argcount):
                if verbose:
                    print>>log, 'Testing %s' % name
                try:
                    total_tested += 1
                    obj()
                except Exception, e:
                    total_failed += 1
                    print>>sys.stderr, '%s.%sFAILED' % (modulename, name)
                    traceback.print_exc()
    message = 'Module %s failed %s out of %s unittests.' % (modulename, total_failed, total_tested)
    if total_failed:
        raise TestException(message)
    if verbose:
        print>>log, message
def __test__():
    print 'in __test__'
#import pretest
#pretest.pretest('microtest', verbose=True)

'''
8.9 自动运行单元测试
'''
# 你想确保在每次编译模块是模块的单元测试会自动运行
# 执行测试的工作最好留给测试运行函数来做，如同8.8节介绍的microtest.test
# 为了让其自动化，可以将下列代码存为模块文件pretest.py，并放入你的Python的sys.path中
import os, sys, microtest
def pretest(modulename, force=False, deleteOnFail=False, runner=microtest.test, verbose=False, log=sys.stdout):
    module = __import__(modulename)
    # 仅测试未编译的模块，除非强制
    if force or module.__file__.endswith('.py'):
        if runner(modulename, verbose, log):
            pass
    elif deleteOnFail:
        # 移除pyc文件以便下次运行测试套件
        filename = module.__file__
        if filename.endswith('.py'):
            filename = filename + 'c'
        try: os.remove(filename)
        except OSError: pass
 # 现在，可以将下列代码放入你的各个模块中
 # import pretest
 # if __name__ != '__main__': # 当模块导入时，不作为主脚本运行
 #     pretest.pretest(__name)

'''
8.10 在Python2.4中使用doctest和unittest
'''
'''
8.11 在单元测试中检查区间
'''
import unittest
class IntervalTestCase(unittest.TestCase):
    def failUnlessInside(self, first, second, error, msg=None):
        #如果first不在区间中，失败区间由second+-error构成
        if not(second-error) < first < (second-error):
            raise self.failureException, (msg or '%r != %r (+-%r)' % (first, second, error))
    def failIfInside(self, first, second, error, msg=None):
        #如果first不在区间中，失败区间由second+-error构成
        if (second-error) < first < (second-error):
            raise self.failureException, ((msg or '%r == %r (+-%r)' % (first, second, error)))
    asserInside = failUnlessInside
    asserNotInside = failIfInside

'''
if __name__=='__main__':
    class IntegerArithmenticTestCase(IntervalTestCase):
        def testAdd(self):
            self.asserInside((1 + 2), 3.3, 0.5)
            self.asserInside(0 + 1, 1.1, 0.01)
        def testMultiply(self):
            self.asserNotInside((0 * 10), .1, .05)
            self.asserNotInside((5 * 8), 40.1, .2)
    unittest.main()
'''