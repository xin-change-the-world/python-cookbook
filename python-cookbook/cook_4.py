#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第四章 Python技巧
# Auther：张广欣
# Date：2014-06-10
#
#
'''
###############################
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