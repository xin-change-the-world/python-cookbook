#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第五章 搜索和排序
# Writer：xin.change.the.world@gmail.com
# Date：2014-06-11
# github: https://github.com/xin-change-the-world/python-cookbook
#
'''
"""
5.1　对字典排序 185
5.2　不区分大小写对字符串列表排序 185
5.3　根据对象的属性将对象列表排序 187
5.4　根据对应值将键或索引排序 189
5.5　根据内嵌的数字将字符串排序 192
5.6　以随机顺序处理列表的元素 193
5.7　在增加元素时保持序列的顺序 195
5.8　获取序列中最小的几个元素 197
5.9　在排序完毕的序列中寻找元素 199
5.10　选取序列中最小的第n个元素 200
5.11　三行代码的快速排序 203
5.12　检查序列的成员 206
5.13　寻找子序列 208
5.14　给字典类型增加排名功能 210
5.15　根据姓的首字母将人名排序和分组 214
"""
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
'''
import bisect
x_insert_point = bisect.bisect_right(L, x)
x_is_present = L[x_insert_point-1:x_insert_point] == [x]
'''
#对Python来说，在列表L中寻找一个元素x是很简单的任务，要检查元素是否存在：
#if x in L;要知道x的确切位置，L.index(x)。然后L的长度为n，这些操作所花费的时间与n成正比，因为他们只是循环地检查每一个元素，看看与x是否相等。其实L是排序过的，我们还可以做的更好。
#在完成了排序的序列中寻找元素的最经典的算法就是二分搜索，一般情况下只需要log2n步就可以完成。

'''
5.10 选取序列中最小的第n个元素
'''
print "=============================   5.10   ============================"
#需要根据排名顺序从序列中获得第n个元素
#如果序列是已经排序的状态，应该使用seq[n]，但如果序列还未被排序，那么除了先对整个序列排序之外，还有没有更好的方法？
import random
def select(data, n):
    '''寻找第n个元素（最小的元素是第0个）'''
    #创建一个新列表，处理小于0的索引，检查索引的有效性
    data = list(data)
    if n < 0:
        n += len(data)
    if not 0 <= n < len(data):
        raise ValueError, "can't get rank %d out of %d" % (n, len(data))
    #主循环，看上去类似于快速排序但不需要递归
    while True:
        pivot = random.choice(data)
        print pivot
        pcount = 0
        under, over = [], []
        uappend, oappend = under.append, over.append
        for elem in data:
            if elem < pivot:
                uappend(elem)
            elif elem > pivot:
                oappend(elem)
            else:
                pcount += 1
        numunder = len(under)
        if n < numunder:
            data = under
        elif n < numunder + pcount:
            return pivot
        else:
            data = over
            n -= numunder + pcount


        
data = [1, 3, 5, 8, 13, 16]
n = 5
print select(data, n)

'''
5.11 三行代码的快速排序
'''
print "=============================   5.11   ============================"
#你想证明python对函数式编程范式的支持比第一眼看上去的印象强多了
def qsort(L):
    if len(L) <= 1: return L
    return qsort([lt for lt in L[1:] if lt < L[0:1]]) + L[0:1] + qsort([ge for ge in L[1:] if ge >= L[0]])
def qs_test(length):
    import random
    joe = range(length)
    random.shuffle(joe)
    print joe
    qsJoe = qsort(joe)
    print qsJoe
    for i in range(len(qsJoe)):
        assert qsJoe[i] == i, 'qsort is broken at %d!' %i
#相比于快速排序的原生实现，我们给出的实现能展现列表推导的强大表现力。
#但千万不要在真是的代码中使用这种方法，Python列表有一个sort方法，速度比我们的实现快得多
'''
def qsort(L):
    if not L: return L
    pivot = L[0]
    def lt(x): return x < pivot
    def ge(x): return x >= pivot
    return qsort(filter(lt, L[1:])) + [pivot] + qsort(filter(ge, L[1:]))
#一旦沿着这条思路走下去，就可以很容易对原来的做法继续改进，比如使用一个随机的轴心元素来尽可能避免最糟糕的情况，并对选用的轴心技术，来应对序列中有太多相等地元素的情况
import random
def qsort(L):
    if not L: return L
    pivot = random.choice(L)
    def lt(x): return x < pivot
    def gt(x): return x > pivot
    return qsort(filter(lt, L)) + [pivot] * L.count(pivot) + qsort(filter(gt, L))

def q(x):
    if len(x)>1:
        lt = [i for i in x if cmp(i,x[0]) == -1]
        eq = [i for i in x if cmp(i,x[0]) == 0]
        gt = [i for i in x if cmp(i,x[0]) == 1]
        return q(lt) + eq + q(gt)
    else:
        return x
'''

'''
5.12 检查序列的成员
'''
#你需要对一个列表执行很频繁的成员资格检查。而in操作符的O(n)时间复杂度对性能的影响很大，你也不能将序列转化为一个字典或者集合，因为你还需要保留原序列的元素顺序
#假设需要给列表添加一个在该列表中不存在的元素。一个可行的办法是写这样一个函数：
def addUnique(baseList, otherList):
    auxDict = dict.fromkeys(baseList)
    for item in otherList:
        if item not in auxDict:
            baseList.append(item)
            auxDict[item] = None
#下面给出一个简单（天真？）的方式，看上去相当不错：
def addUnique_simple(baseList, otherList):
    for item in otherList:
        if item not in baseList:
            baseList.append(item)
#如果列表不是很短，这个简单的方法会非常慢。判断 if item not in baseList会遍历baseList，消耗的时间正比于这两个列表的乘积
#而addUnique函数，首先创建了一个辅助的字典auxDict，这一步的时间正比于len(baseList)然后在循环中检查dict的成员——这是造成巨大差异的一部，因为检查一个元素是否处于一个dict中的时间大致是一个常数，而于dict中元素的数目没有关系。
#因此那个for循环消耗的时间正比于len(otherList)，这样整个函数所需要的时间久正比于这两个列表的长度之和

'''
5.13 寻找子序列
'''
#你需要在大序列中查找子序列
#如果序列式字符串（普通的或者Unicode）Python的字符串的find方法以及标准库的re模块式最好的工具。否则，应该使用Knuth-Morris-Pratt算法（KMP）：
def KnuthMorrisPratt(text, pattern):
    '''
    #在序列text中找到pattern的子序列的起始位置，
    #每个参数都可以是任何可迭代对象
    #在每次产生一个结果时，对text的读取正好到达（包括）对pattern的一个匹配
    '''
    #确保能对pattern进行索引操作，同时制作pattern的一个拷贝，以防在生成结果时意外地修改pattern
    pattern = list(pattern)
    length = len(pattern)
    #创建KMP"偏移量表"并命名为shifts
    shifts = [1] * (length + 1)
    shift = 1
    for pos, pat in enumerate(pattern):
        while shift <= pos and pat != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift
    #执行真正的搜索
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == length or matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == length: yield startPos

'''
5.14 给字典类型增加排名功能
'''
#你需要用字典存储一些键和“分数”的映射关系。你经常需要以自然顺序（即以分数的升序）
#访问键和分数值，并能够根据那个顺序检查一个键的排名。对于这个问题，用dict似乎不太合适
#!/usr/bin/env python
'''一个反映键到分数的映射的字典'''
from bisect import bisect_left, insort_left
import UserDict
class Ratings(UserDict.DictMixin, dict):
    """
    #Ratings类很像一个字典，但有一些额外特性：每个键的对应值都是该键的分数，所有键都根据他们的分数排名
    #对应值必须是可以比较的，同样，键则必须是可哈希的（即可以“绑”在分数上）
    """
    def __init__(self, *args, **kwds):
        '''这个类就像dict一样被实例化'''
        dict.__init__(self, *args, **kwds)
        #self._rating是关键的辅助数据结构：一个所有（值，键）的列表，并保有一种“自然的”排序状态
        self._rating = [ (v, k) for k, v in dict.iteritems(self) ]
        self._rating.sort()
    def copy(self):
        '''提供一个完全相同但独立的拷贝'''
        return Ratings(self)
    def __setitem__(self, k, v):
        '''除了把主要任务委托给dict，我们还维护self._rating'''
        if k in self:
            del self._rating[self.rating(k)]
        dict.__setitem__(self, k, v)
        insort_left(self._rating, (v, k))
    def __delitem__(self, k):
        '''除了把主要任务委托给dict，我们还维护self._rating'''
        del self._rating[self.rating(k)]
        dict.__delitem__(self,k)
        '''显式地将某些方法委托给dict的对应方法，以免继承了DictMixin的较慢的（虽然功能正确）实现'''
        __len__ = dict.__len__
        __contains__ = dict.__contains__
        has_key = __contains__
        '''在self._rating 和self.keys()之间的关键的语义联系——DictMixin免费给我了门所有其他方法，虽然我们直接实现他们能够获得稍好一点的性能'''
    def __iter__(self):
        for v, k in self._rating:
            yield k
        iterkeys = __iter__
    def keys(self):
        return list(self)
    '''三个和排名相关的方法'''
    def rating(self, key):
        item = self[key], key
        i = bisect_left(self._rating, item)
        if item == self._rating[i]:
            return i
        raise LookupError, "item not found in rating"
    def getValueByRating(self, rating):
        return self._rating[rating][0]
    def getKeyByRating(self, rating):
        return self._rating[rating][1]
def test():
    '''
    #我们使用doctest来测试这个模块，模块名必须为rating.py这样docstring中的实例才会有效
    '''
    import doctest, rating
    doctest.testmod(rating)


r = Ratings({"bob": 30, "john": 30})
print len(r)
print r.has_key("paul"), "paul" in r
r["john"] = 20
r.update({"paul": 20, "tom": 10})
print len(r), r

'''
5.15 根据姓的首字母将人名排序和分组
'''
'''
itertools模块包含创建有效迭代器的函数，可以用各种方式对数据进行循环操作，此模块中的所有函数返回的迭代器都可以与for循环语句以及其他包含迭代器（如生成器和生成器表达式）的函数联合使用。
groupby(iterable [,key]):

创建一个迭代器，对iterable生成的连续项进行分组，在分组过程中会查找重复项。

如果iterable在多次连续迭代中生成了同一项，则会定义一个组，如果将此函数应用一个分类列表，那么分组将定义该列表中的所有唯一项，key（如果已提供）是一个函数，应用于每一项，如果此函数存在返回值，该值将用于后续项而不是该项本身进行比较，此函数返回的迭代器生成元素(key, group)，其中key是分组的键值，group是迭代器，生成组成该组的所有项。

'''
import itertools
def groupnames(name_iterable):
    sorted_names = sorted(name_iterable, key=_sortkeyfunc)
    name_dict = {}
    for key, group in itertools.groupby(sorted_names, _groupkeyfunc):
        name_dict[key] = tuple(group)
    return name_dict
pieces_order = { 2: (-1, 0), 3: (-1, 0, 1) }

def _sortkeyfunc(name):
    '''
    #name是带有名和姓以及可选的中名或首字母的字符串，这些部分之间用空格隔开；返回的字符串的顺序是姓-名-中名，以满足排序的需要
    '''
    name_parts = name.split()
    return ''.join([name_parts[n] for n in pieces_order[len(name_parts)]])
def _groupkeyfunc(name):
    '''返回的键（即姓的首字母）被用于分组'''
    return name.split()[-1][0]

