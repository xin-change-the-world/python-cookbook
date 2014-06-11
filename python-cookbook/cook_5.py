#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第五章 搜索和排序
# Auther：张广欣
# Date：2014-06-11
#
#
'''
###############################
#Python2.3中的提姆排序（timsort）是稳定的，健壮的，而且在实际应用中也快的像飞一样
'''
5.1 对字典排序
'''
#你想对字典排序，这可能意味着需要先根据字典的键排序，然后再让对应值也处于同样的顺序
def sortedDictValues(adict):
	keys = adict.keys()
	keys.sort()
	#return [adict[key] for key in keys]
	#效率更高的写法
	return map(adict.get, keys)

'''
5.2 不区分大小写对字符串列表排序
'''
def case_insensitive_sort(string_list):
	auxiliary_list = [(x.lower(), x) for x in string_list]
	auxiliary_list.sort()
	return [x[1] for x in auxiliary_list]
#Python2.4已经提供对DSU的原生支持了，因此（假设string_list的元素都是真正的普通字符串，而不是Unicode对象之类）可以用更简短更快的方式
def case_insensitive_sort2(string_list):
	return sorted(string_list, key=str.lower)
print case_insensitive_sort(['d','B','C','a','E'])
#一个很明显的可选方案是编写一个比较函数，并将其传递给sort方法
def case_insensitive_sort1(string_list):
	def compare(a, b): return cmp(a.lower(), b.lower())
	string_list.sort(compare)
'''
5.3 根据对象的属性将对象列表排序
'''
#根据对象的某个属性来完成对整个对象列表的排序
def sort_by_attr(seq, attr):
	intermed = [ (getattr(x, attr), i, x) for i, x in enumerate(seq) ]
	intermed.sort()
	return [ x[-1] for x in intermed ]
def sort_by_attr_inplace(lst, attr):
	lst[:] = sort_by_attr(lst, attr)

'''
由于Python2.4的对DSU的原生支持，代码可以写得更短，跑的更快
import operator
def sort_by_attr(seq, attr):
	return sorted(seq, key=operator.attrgetter(attr))
def sort_by_attr_inplace(lst, attr):
	lst.sort(key=operator.attrgetter(attr))
'''

'''
5.4 根据对应值将键或索引排序
'''
#需要统计不同元素出现的次数，并且根据他们的出现次数安排他们的顺序——比如，你想制作一个柱状图
class hist(dict):
	def add(self, item, increment=1):
		'''为item的条目增加计数'''
		self[item] = increment + self.get(item, 0)
	def counts(self, reverse=False):
		'''返回根据对应值排序的键的列表'''
		aux = [ (self[k], k) for k in self ]
		aux.sort()
		if reverse: aux.reverse()
		return [k for v, k in aux]
#如果想将元素的统计结果放到一个列表中，做法也非常类似：
class hist1(list):
	def __init__(self, n):
		'''初始化列表，统计n个不同项的出现'''
		list.__init__(self, n*[0])
	def add(self, item, increment=1):
		'''为item的条目增加计数'''
		self[item] += increment
	def counts(self, reverse=False):
		'''返回根基对应值排序的索引的列表'''
		aux = [ (v, k) for k, v in enumerate(self) ]
		aux.sort()
		if reverse: aux.reverse()
		return [k for v, k in aux]

'''
#如果我们想要在自己的程序中使用这两个类，由于他们的相似性，我们应该进行代码重构
#从中分离出共性，并置入一个单独的辅助函数_sorted_keys

def _sorted_keys(container, keys, reverse):
	#返回keys的列表，根据container中的对应值排序
	aux = [ (container[k], k) for k in keys ]
	aux.sort()
	if reverse: aux.reverse()
	return [k for v, k in aux]

class hist(dict):
	#...
	def counts(self, reverse=False):
		return _sorted_keys(self, self, reverse)

class hist1(list):
	#...
	def counts(self, reverse=False):
		return _sorted_keys(self, xrange(len(self)), reverse)
#DSU在Python2.4中非常重要，列表sort方法和新的内建的sorted函数提供了一个快速的、原生的DSU实现。
#因此在Python2.4中，_sorted_keys还可以变得更简单快速
def _sorted_keys(container, keys, reverse):
	return sorted(keys, key=container.__getitem__, reverse=reverse)
'''
#Python2.4还提供了一个简单直接的方法获取字典元素根据值排序后的列表
from operator import itemgetter
def dict_items_sorted_by_value(d, reverse=False):
	return sorted(d.iteritems(), key=itemgetter(1), reverse=reverse)

sentence = '''
	Hello there this is a test. Hello there this was a test, but now it is not.
'''
words = sentence.split()
c = hist()
for word in words: c.add(word)
print "Ascending count:"
print c.counts()
print "Descending count:"
print c.counts(reverse=True)

'''
5.5 根据内嵌的数字将字符串排序
'''
#你想将一个字符串列表进行排序，这些字符串都含有数字的子串
#比如foo2.txt应该在foo10.txt前面，而Python默认的字符串比较是基于字母顺序的，所以默认情况下foo10.txt会在foo2.txt前面
#需要先将每个字符串切割开，形成数字和非数字的序列，然后将每个序列中的数字转换成一个数，这会产生一个数的列表，可以用来做排序时比较的键
import re
re_digits = re.compile(r'(\d+)')
def embedded_numbers(s):
    pieces = re_digits.split(s)             # 切成数字与非数字
    pieces[1::2] = map(int, pieces[1::2])   # 将数字部分转成整数

    return pieces
def sort_strings_with_embedded_numbers(alist):
    aux = [ (embedded_numbers(s), s) for s in alist ]
    aux.sort()

    return [ s for __, s in aux ]            #__意味着忽略  

#在Python2.4中，用相同的ebbedded_numbers函数，加上DSU支持，代码编程
'''
def sort_strings_with_embedded_numbers(alist):
	return sorted(alist, key=embedded_numbers)
'''
files = ['file11.txt', 'file15.txt', 'file3.txt', 'file4.txt']
print ' '.join(sort_strings_with_embedded_numbers(files))

'''
5.6 以随机顺序处理列表的元素
'''
#你想以随机的顺序处理一个很长的列表
def process_all_in_random_order(data, process):
	#  首先，将整个列表置于随机顺序
	random.shuffle(data)
	for elem in data: process(elem)

#假设我们必须以随机顺序处理一个不重复的长列表的元素
#第一个想法可能会是这样：我们可以反复地、随机地挑出元素（通过random.choice函数）
#并将原列表中被挑选的元素删除，以避免重复挑选
import random
def process_random_removing(data, process):
	while data:
		elem = random.choice(data)
		data.remove(elem)
		process(elem)
#然而这个函数慢的可怕，即使输入列表只有几百个元素。每个data.remove调用都会线性地搜索整个列表以获取要删除的元素
#由于第n步的时间消耗是O(n)因此整个处理过程的消耗时间是O(n2)正比于列表长度的平方
d = dict(enumerate('ciao'))
while d: print d.popitem()

'''
5.7 在增加元素时保持序列的顺序
'''
#你需要维护一个序列，这个序列不断地有新元素加入，但始终处于排序完毕的状态，这样你可以再任何需要的时候检查或者删除当前序列中最小的元素
the_list = [903, 10, 35, 69, 933, 485, 519, 379, 102, 402, 883, 1]
#可以调用the_list.sort()将列表排序，然后用result=the_list.pop(0)来获得和删除最小的元素。
#但是每当加入一个元素（比如the_list.append(0)）都需要再次调用the_list.sort()来排序
#可以使用Python标准库的heapq模块
import heapq
heapq.heapify(the_list)
#现在列表并不一定完成了排序，但是它却满足堆的特性（若所有涉及的索引都是有效的，则the_list[i] <= the_list[2*i + 1] 且 the_list[i] <= the_list[2*i+2]）
#为了保持堆特性的有效性，我们使用result=heapq.heappop(the_list)来获取并删除最小的元素，用heapq.heappush(the_list, newitem)来加入新的元素
#如果需要同时做这两件事，加入一个新元素并删除之前的最小的元素，可以使用result=heapq.heapreplace(the_list, newitem)

'''
5.8 获取序列中最小的几个元素
'''
#可以将序列排序，然后使用seq[:n]
#如果需要的元素数目n远小于序列的长度，我们获取前n个最小元素的时间是O(n)
#下面给出一个简单可行的生成器，在Python2.3和2.4中都同样有效：
import heapq
def isorted(data):
	data = list(data)
	heapq.heapify(data)
	while data:
		yield heapq.heappop(data)

#在Python2.4中，如果事先知道n，还有更简单和更快的方法从data中获取前n个最小的元素：
import heapq
def smallest(n, data):
	return heapq.nsmallest(n, data)

'''
5.9 在排序完毕的序列中寻找元素
'''
#如果L已经是排序完毕的状态，则Python标准库提供的bisect模块可以很容易滴检查出元素x是否在L中：
import bisect
x_insert_point = bisect.bisect_right(L, x)
x_is_present = L[x_insert_point-1:x_insert_point] == [x]