#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第四章 Python技巧
# Writer：xin.change.the.world@gmail.com
# Date：2014-06-10
#
#
'''
"""
4.1　对象拷贝 140
4.2　通过列表推导构建列表 144
4.3　若列表中某元素存在则返回之 146
4.4　循环访问序列中的元素和索引 147
4.5　在无须共享引用的条件下创建列表的列表 148
4.6　展开一个嵌套的序列 149
4.7　在行列表中完成对列的删除和排序 152
4.8　二维阵列变换 154
4.9　从字典中取值 155
4.10　给字典增加一个条目 157
4.11　在无须过多援引的情况下创建字典 158
4.12　将列表元素交替地作为键和值来创建字典 159
4.13　获取字典的一个子集 161
4.14　反转字典 163
4.15　字典的一键多值 164
4.16　用字典分派方法和函数 166
4.17　字典的并集与交集 167
4.18　搜集命名的子项 169
4.19　用一条语句完成赋值和测试 171
4.20　在Python中使用printf 174
4.21　以指定的概率获取元素 174
4.22　在表达式中处理异常 176
4.23　确保名字已经在给定模块中被定义 178
"""
'''
4.1 对象拷贝
'''
#你想拷贝某对象，不过，当你对一个对象赋值，将其作为参数传递，或者作为
#结果返回时，Python通常会使用指向原对象的而引用，而不是真正的拷贝
import copy
existing_list = [1,2,3]
new_list = copy.copy(existing_list)
#某些时候，你可能需要对象中的属性和内容被分别的和递归的拷贝，可以使用deepcopy
existing_list_of_dicts = [{1:{'a':2}}]
new_list_of_dicts = copy.deepcopy(existing_list_of_dicts)

a = [1,2,3]
b = a
b.append(5)
print a
print b
#copy.copy：浅拷贝，对象内部属性和内容依然引用原对象，快而且节省内存
list_of_lists = [ ['a'], [1, 2], ['z', 23] ]
copy_lol = copy.copy(list_of_lists)
copy_lol[1].append('boo')
print list_of_lists, copy_lol
#copy.deepcopy：递归的拷贝内部引用的对象（所有的元素，属性，元素的元素，元素的属性），消耗相当的时间和内存

'''
4.2 通过列表推到构建列表
'''
#你想通过操作和处理一个序列（或其他的可迭代对象）中的元素来创建一个新的列表
theoldlist = [1, 2, 3]
thenewlist = [x + 23 for x in theoldlist]
thenewlist = [x for x in theoldlist if x > 2]
thenewlist = [x + 23 for x in theoldlist if x > 2]
#将L中所有大于100的元素设置成100
L = [10, 99, 100, 101, 102]
L[:] = [min(x, 100) for x in L]
print L

'''
4.3 若列表中某元素存在则返回之
'''
def list_get(L, i, v=None):
    if -len(L) <- i < len(L):return L[i]
    else: return v
#另一种方式
def list_get_egfp(L, i, v=None):
    try: return L[i]
    except IndexError: return v
#第二种方法比第一种慢四倍

'''
4.4 循环访问序列中的元素和索引
'''
#需要循环访问一个序列，并且每一步都需要知道已经访问到的索引
def transform(x):
    print x
sequence = {0:'a', 1:'b', 2:'c'}
for index, item in enumerate(sequence):
	if item > 23:
		sequence[index] = transform(item)
#比以下这种方式更快
for index in range(len(sequence)):
	if sequence[index] > 23:
		sequence[index] = transform(sequence[index])

'''
4.5 在无须共享引用的条件下创建列表的列表
'''
#你想创建一个多维度的列表，且同时避免隐式的引用共享
multilist = [[0 for col in range(5)] for row in range(10)]
print multilist

'''
4.6 展开一个嵌套的序列
'''
def list_or_tuple(x):
	return isinstance(x, (list, tuple))
def flatten(sequence, to_expand=list_or_tuple):
	for item in sequence:
		if to_expand(item):
			for subitem in flatten(item, to_expand):
				yield subitem
		else:
			yield item
sequence = [1, 2, [3, [], 4, [5, 6]]]
for s in flatten(sequence):
	print s

'''
4.7 在行列表中完成对列的删除和排序
'''
#你有一个包含列表（行）的列表，现在你想获得另一个列表，该列表包含了同样的行
#但是其中一些列被删除或者重新排序了
#列表推导很适合这个任务
#假设你有这样一个列表
listOfRows = [ [1,2,3,4], [5,6,7,8], [9,10,11,12] ]
#需要另一个有同样行的列表，但是其中第二列被删除了，第三和第四列互换了位置
newList = [ [row[0], row[3], row[2]] for row in listOfRows ]
print newList
#或者
newList = [ [row[ci] for ci in (0, 3, 2)] for row in listOfRows ]
#列表推导会产生一个新的列表而不是修改现有的列表，当需要修改一个现有的列表时，最好的办法是将现有的列表的内容赋值为一个列表推导
listOfRows[:] = [ [row[0], row[3], row[2]] for row in listOfRows ]

'''
4.8 二维阵列变换
'''
#需要变换一个列表的列表，将行换成列，列换成行
arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
print [[r[col] for r in arr] for col in range(len(arr[0]))]
#另一种方法
print map(list, zip(*arr))
#如果需要转换非常巨大的数字阵列，可以考虑Numeric Python和其他第三方包

'''
4.9 从字典中取值
'''
#你想从字典中取值，但是又不想由于你搜索的键不存在而处理异常。
d = {'a':'first'}
print d.get('b', 'not found')

'''
4.10 给字典增加一个条目
'''
#给定一个字典d，当k是字典的键时，你想直接使用d[k]，若k不是d的键，则增加新条目d[k]
#字典的setdefault方法正是为此而设计的。
def addword(theIndex, word, pagenumber):
    theIndex.setdefault(word, []).append(pagenumber)
#这段代码等价于下面的：
def addword2(theIndex, word, pagenumber):
	if word in theIndex:
		theIndex[word].append(pagenumber)
	else:
		theIndex[word] = [pagenumber]

'''
4.11 在无须过多援引的情况下创建字典
'''
#当你逐渐习惯了Python，会发现自己已经创建了大量的字典。
#当键时标识符时，可以用dict加上明明的参数来避免援引他们：（除关键字和数字开头）
data = dict(red=1, green=2, blue=3)
#这看上去比直接用字典形式的语法要整洁一些：
data = {'red': 1, 'green': 2, 'blue': 3}
#当d不是一个字典，而是一个数对(key, value)的序列时dict(d)仍然有效
'''
d = dict(zip(the_keys, the_values))
如果序列非常长，那么用Python标准库中的itertoos模块能有效的提高速度：
import itertools
d = dict(itertools.izip(the_keys, the_values))
长度为10000的序列，第二种方式快两倍左右
'''

'''
4.12 将列表元素交替地作为键和值来创建字典
'''
#给定一个列表，需要交替的使用列表中的元素作为键和对应值来创建一个字典
def dictFromList(keysAndValues):
	return dict(zip(keysAndValues[::2], keysAndValues[1::2]))
#方法2，把从给定序列中获取多个数对的过程独立出来，变成一个单独的生成器
def pairwise(iterable):
	itnext = iter(iterable).next
	while True:
		yield itnext(), itnext()
def dictFromSequence(seq):
	return dict(pairwise(seq))

'''
4.13 获取字典的一个子集
'''
#你有一个巨大的字典，字典中的一些键属于一个特定的集合，而你想创建一个包含这个键集合及其对应值的新字典
#如果你不想改动原字典
def sub_dict(somedict, somekeys, default=None):
	return dict([ (k, somedict.get(k, default)) for k in somekeys ])
#如果你从原字典删除那些符合条件的条目：
def sub_dict_remove(somedict, somekeys, default=None):
	return dict( [ (k, somedict.pop(k, default)) for k in somekeys ] )

d = {'a':5, 'b':6, 'c':7}
print sub_dict(d, 'ab'), d
print sub_dict_remove(d, 'ab'), d
#键不匹配时，得到异常提醒
def sub_dict_strict(somedict, somekeys):
    return dict([ (k, somedict[k]) for k in somekeys ])
def sub_dict_remove_strict(somedict, somekeys):
    return dict([ (k, somedict.pop(k)) for k in somekeys ])
#键不匹配时，直接忽略
def sub_dict_select(somedict, somekeys):
    return dict([ (k, somedict[k]) for k in somekeys if k in somedict ])
def sub_dict_remove_select(somedict, somekeys):
    return dict([ (k, somedict.pop(k)) for k in somekeys if k in somedict ])


'''
4.14 反转字典
'''
#给定一个字典，此字典将不同的键映射到不同的值。而你想创建一个反转的字典，将各个值反映射到键
def invert_dict(d):
	return dict([ (v, k) for k, v in d.iteritems() ])
#对于比较大的字典，用Python标准库itertools模块提供的izip会更快一些
from itertools import izip
def invert_dict_fast(d):
	return dict(izip(d.itervalues(), d.iterkeys()))

'''
4.15 字典的一键多值
'''
#需要一个字典，能够将每个键映射到多个值上
#正常情况下，字典是一对一映射的，但要实现一对多映射也不难，换句话说，即一个键对应多个值。
#你有两个可选方案，但具体要看你怎么看待键的多个对应值的重复。下面这种方法，使用list作为dict的值，允许重复
'''
d1 = {}
d1.setdefault(key, []).append(value)
#另一种方案，使用子字典作为dict的值，自然而然地消灭了值重复的可能
d2 = {}
d2.setdefault(key, {})[value] = 1
#在python2.4中，这种无重复值的方法可等价地被修改为：
d3 = {}
d3.setdefault(key, set()).add(value)
'''

'''
4.16 用字典分派方法和函数
'''
#需要根据某个控制变量的值执行不同的代码片段——在其他的语言中你可能会使用case语句
#归功于面向对象编程的优雅的分派概念，case语句的使用大多（但不是所有）都可以被替换成其他分派形式。在python中
#字典及函数都是一等（first－class）对象这个事实（比如函数可以作为字典中的值被存储）
#使得case语句的问题更容易被解决
print "===================="
animals = []
number_of_felines = 0
def deal_with_a_cat():
	global number_of_felines
	print "meow"
	animals.append('feline')
	number_of_felines += 1
def deal_with_a_dog():
	print "bark"
	animals.append('canine')
def deal_with_a_bear():
	print "watch out for the *HUG*"
	animals.append('ursine')
tokenDict = {
	"cat": deal_with_a_cat,
	"dog": deal_with_a_dog,
	"bear": deal_with_a_bear,
}
#模拟，比如，从文件中读取的一些单词
words = {"cat", "bear", "cat", "dog"}
for word in words:
	#查找每个单词对应的函数调用并调用之
	tokenDict[word]()
nf = number_of_felines
print 'we met %d feline%s' % (nf, 's'[nf==1:])
print 'the animals we met were:', ' '.join(animals)

'''
4.17 字典的并集与交集
'''
#在这个要求中，只需要考虑键，不需要考虑键的对应值，一般可以通过调用dict.fromkeys来创建字典
a = dict.fromkeys(xrange(1000))
b = dict.fromkeys(xrange(500, 1500))
#最快计算出并集的方法是：
union = dict(a, **b)
#最快且最简洁地获得交集的方法是：
inter = dict.fromkeys([x for x in a if x in b])

#如果字典a和b的条目差异很大，那么在for字句中用较短的那个字典，在if子句中用较长的字典会有利于提升运算速度
if len(a) < len(b):
	inter = dict.fromkeys([x for x in a if x not in b])
else:
	inter = dict.fromkeys([x for x in b if x not in a ])

#python也提供了直接代表集合的类型set模块，2.3和2.4都可以使用下面的代码
try:
	set
except NameError:
	from sets import Set as set

#这样做的好处是，可以到处使用set类型，同时还获得了清晰和简洁，以及速度的提升，在python2.4中：
a = set(xrange(1000))
b = set(xrange(500, 1500))
union = a | b #a.union(b)
inter = a & b #a.intersection(b)

#即使由于某些原因使用了dict，也应当尽可能地用set来完成集合操作。举个例子，假设你有个字典phones，将人名映射到电话号码，还有个字典address，将人名映射到地址。
#最清楚简单地打印所有同时知道地址和电话号码的人名及其相关数据的方式：
for name in set(phones) & set(addresses):
	print name, phones[name], addresses[name]
#跟下面的方法比，这非常简洁，虽然清晰度可能还有争议
for name in phones:
	if name in address:
		print name, phones[name], address[name]
#另一个很好的可选方法是：
for name in set(phones).intersection(addresses):
	print name, phones[name], address[name]

'''
4.18 搜集命名的子项
'''
#你想搜集一系列的子项，并命名这些子项，而且你认为用字典来实现有点不便。
#任意一个类的实例都继承了一个被封装到内部的字典，它用这个字典来记录自己的状态。
class Bunch(object):
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
point = Bunch(datum=y, squared=y*y, coord=x)
#现在就可以访问并重新绑定那些刚被创建的命名属性了，也可以进行添加，移除某些属性之类的操作
if point.squared > threshold:
	point.isok = True