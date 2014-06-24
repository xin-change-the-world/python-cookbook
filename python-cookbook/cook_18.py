#!/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第十八章 算法 616
# Writer：xin.change.the.world@gmail.com
# Date：2014-06-24
# github: https://github.com/xin-change-the-world/python-cookbook
#
'''
'''
引言 616
18.1　消除序列中的重复 619
18.2　在保留序列顺序的前提下消除其中的重复 621
18.3　生成回置采样 625
18.4　生成无回置的抽样 626
18.5　缓存函数的返回值 627
18.6　实现一个FIFO容器 629
18.7　使用FIFO策略来缓存对象 631
18.8　实现一个Bag（Multiset）收集类型 634
18.9　在Python模拟三元操作符 637
18.10　计算素数 640
18.11　将整数格式化为二进制字符串 642
18.12　以任意数为基将整数格式化为字符串 644
18.13　通过法雷分数将数字转成有理数 646
18.14　带误差传递的数学计算 648
18.15　以最大精度求和 651
18.16　模拟浮点数 653
18.17　计算二维点集的凸包和直径 656
'''
'''
18.1 消除序列中的重复
'''
# 你有一个可能含有重复子项的序列，而你想以最快速的方法消除其中的重复，同时还不用了解很多关于序列中的元素属性的信息。，此外，你并不关心最后的结果序列中的元素顺序
# 兼容2.3,2.4
try: set
except NameError: from sets import Set as set
def unique(s):
    """
    # 返回一个无序的列表，其中没有重复
    # 首先使用set，因为这通常是最快的可行方法
    """
    try:
        return list(set(s))
    except TypeError:
        pass # 切换到另一种方法
    # 由于你无法对元素采用哈希，只好尝试排序，这会把相等地元素集中到一起，从而便于删除
    t = list(s)
    try:
        t.sort()
    except TypeError:
        del t # 换到另一种方法
    else:
        # 排序可行，这很好，删除重复项
        return [x for i, x in enumerate(t) if not i or x != t[i-1]]
    # 暴力法是最后的手段
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

'''
18.2 在保留序列顺序的前提下消除其中的重复
'''
try: set
except NameError: from sets import Set as set
# f定义了序列seq的元素之间的等价对应关系，而且对于seq的任意元素
# x，f(x)必须是可哈希的
def uniquer(seq, f=None):
	# 保留由f定义的每个单价类中最早出现的元素
	if f is None: # f默认是身份函数f(x) -> x
	    def f(x): return x
	already_seen = set()
	result = [ ]
	for item in seq:
		marker = f(item)
		if marker not in already_seen:
			already_seen.add(marker)
			result.append(item)
	return result

'''
18.3 生成回置采样
'''
# 你想生成带有回置的随机样本，样本空间是一个序列中的所有项
import random
def sample_wr(population, _choose=random.choice):
	while True: yield _choose(population)

# 举个栗子，生成50个小写ASCII字母的随机字符串
'''
import itertools
from string import ascii_lowercase
x = ''.join(itertools.slice(sample_wr(ascii_lowercase), 50))
print x
'''
# 如果你没有sample_wr生成器，则等价的代码可能会是这样：
from string import ascii_lowercase
from random import choice
x = ''.join([ random.choice(ascii_lowercase) for i in xrange(50)])
print x

'''
18.4 生成无回置的抽样
'''
# 你想生成带有回置的采样，样本空间是一个序列中所有的项，而且你希望能拥有比random.sample更好的内存效率。
import random
def sample(n, r):
	# 生成r个从[0, n]随机挑选并排序的整数
	rand = random.random
	pop = n
	for samp in xrange(r, 0, -1):
		cumprob = 1.0
		x = rand()
		while x < cumprob:
			cumprob -= cumprob * samp / pop
			pop -= 1
		yield n-pop-1

'''
18.5 缓存函数的返回值
'''
# 你有个纯函数（只依赖输入的参数，没有其他数据输入渠道（全局变量之类））而返回值也是它唯一的输出。
# 你通常总是用相同的参数（特别是递归函数）来调用它，而且计算时间很长，你希望找到一个简单地办法提升性能
# 缓存化的关键西路是将函数的结果存到一个字典中，将产生该结果的调用参数作为字典的键。
fib_memo = {}
def fib(n):
	if n < 2: return 1
	if n not in fib_memo:
		fib_memo[n] = fib(n-1) + fib(n-2)
	return fib_memo[n]
# 但每次在每个函数内部写缓存化代码，这个过程很重复单调，而且还降低了原函数的可读性。
# 一个可选的方案是将缓存化机制封装到一个闭包中
def memoize(fn):
	memo = {}
	def memoizer(*param_tuple, **kwds_dict):
		# 如果有命名参数将无法缓存化
		if kwds_dict:
			return fn(*param_tuple, **kwds_dict)
		try:
			# 试图使用memo字典，若失败则更新之
			try:
				return memo[param_tuple]
			except KeyError:
				memo[param_tuple] = result = fn(*param_tuple)
				return result
		except TypeError:
			# 一些可变的参数，绕过缓存化机制
			return fn(*param_tuple)
	return memoizer

def fib(n):
	if n < 2:return 1
	return fib(n-1) + fib(n-2)
fib = memoize(fib)
# 或者python2.4以上
@memoize
def fib(n):
	if n < 2: return 1
	return fib(n-1) + fib(n-2)

'''
18.6 实现一个FIFP容器
'''
# 需要一个支持插入和删除元素的容器，而且第一个插入的元素也将是第一个被删除的元素（即一个先进先出队列）
class Fifo(list):
	def __init__(self):
		self.back = [ ]
		self.append = self.back.append
	def pop(self):
		if not self:
			self.back.reverse()
			self[:] = self.back
			del self.back[:]
		return super(Fifo, self).pop()
a = Fifo()
a.append(10)
a.append(20)
print a.pop()
a.append(5)
print a.pop()
print a.pop()

# 更简单的方法
class FifoList(list):
	def pop(self):
		return super(FifoList, self).pop(0)
class FifoDict(dict):
	def __init__(self):
		self.nextin = 0
		self.nextout = 0
	def append(self, data):
		self.nextin += 1
		self[self.nextin] = data
	def pop(self):
		self.nextout += 1
		return dict.pop(self, self.nextout)

'''
18.7 使用FIFO策略来缓存对象
'''
import UserDict
class FifoCache(object, UserDict.DictMixin):
	''' 一个能够记住被设置过的条目的映射 '''
	def __init__(self, num_entries, dct=()):
		self.num_entries = num_entries
		self.dct = dict(dct)
		self.lst = []
	def __repr__(self):
		return '%r(%r,%r)' % (self.__class__.__name__, self.num_entries, self.dct)
	def copy(self):
		return self.__class__(self.num_entries, self.dct)
	def keys(self):
		return list(self.lst)
	def __getitem__(self, key):
		return self.dct[key]
	def __setitem__(self, key, value):
		dct = self.dct
		lst = self.lst
		if key in dct:
			lst.remove(key)
		dct[key] = value
		lst.append(key)
		if len(lst) > self.num_entries:
			del dct[lst.pop(0)]
	def __delitem__(self, key):
		self.dct.pop(key)
		self.lst.remove(key)
	# 一个纯粹出于优化目的而被显示定义的方法
	def __contains__(self, item):
		return item in self.dct
	has_key = __contains__
