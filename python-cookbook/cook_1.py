#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第一章 文本
# Writer：张广欣
# Date：2014-06-04
#
#
'''
'''
1.1　每次处理一个字符 6
1.2　字符和字符值之间的转换 7
1.3　测试一个对象是否是类字符串 8
1.4　字符串对齐 10
1.5　去除字符串两端的空格 11
1.6　合并字符串 11
1.7　将字符串逐字符或逐词反转 14
1.8　检查字符串中是否包含某字符集合中的字符 15
1.9　简化字符串的translate方法的使用 18
1.10　过滤字符串中不属于指定集合的字符 20
1.11　检查一个字符串是文本还是二进制 23
1.12　控制大小写 25
1.13　访问子字符串 26
1.14　改变多行文本字符串的缩进 29
1.15　扩展和压缩制表符 31
1.16　替换字符串中的子串 33
1.17　替换字符串中的子串-Python 2.4 34
1.18　一次完成多个替换 36
1.19　检查字符串中的结束标记 39
1.20　使用Unicode来处理国际化文本 40
1.21　在Unicode和普通字符串之间转换 43
1.22　在标准输出中打印Unicode字符 45
1.23　对Unicode数据编码并用于XML和HTML 46
1.24　让某些字符串大小写不敏感 49
1.25　将HTML文档转化为文本显示到UNIX终端上 52
'''
'''
1.1 每次处理一个字符
'''
thestring = "aabbcc"
#可以调用内建的list.
thelist = list(thestring)
print thelist
#['a', 'a', 'b', 'b', 'c', 'c']
#也可以用for循环
for c in thestring:
    print c
#也可以用列表推导中的for遍历
result = [c for c in thestring]
print result
#['a', 'a', 'b', 'b', 'c', 'c']

#获取字符串中所有字符的集合，可以用set

import sets
magic_chars = sets.Set(thestring)
magic_chars2 = sets.Set('aaddeeff')
print ''.join(magic_chars)
#acb
print ''.join(magic_chars & magic_chars2)#集合的交集
#a
'''
1.2 字符和字符值之间的转换
'''
#将一个字符转化为相应的ASC（ISO）或者Unicode码，或者反其道而行之
#这正是内建函数ord和chr擅长的任务
print ord('a')
#97
print chr(97)
#a
print ord(u'\u2020')
#8224
print repr(unichr(8224))
#将一个字符串转化为一个包含各个字符的值的列表
print map(ord, 'python')
#[112, 121, 116, 104, 111, 110]
#通过包含了字符值得列表创建字符串，可以使用''.join、map、chr
print ''.join(map(chr, range(97, 100)))
#abc
'''
1.3 测试一个对象是否是类字符串
'''
def isAString(obj):
    return isinstance(obj, basestring)
print isAString('aaa')
#True
print isAString(123)
#False
#isAString函数无法检测UserString模块提供的UserString类的实例，因为UserString不是从basestring类派生的
#如果想坚持这种类型，可以直接检查一个对象的行为是否真的像字符串一样
def isStringLike(obj):
    try: obj + ''
    except: return False
    else: return True
#此函数比isAString函数要慢的多而且复杂，但是适用于UserString（以及其他的类字符串的类型）的实例，也适用于str和unicode
'''
1.4 字符串对齐
'''
print '|','hej'.ljust(20),'|','hej'.rjust(20),'|','hej'.center(20),'|'
print 'hej'.center(6, '+')
'''
1.5 去除字符串两端的空格
'''
x = '   xin   '
print '|',x.lstrip(),'|',x.rstrip(),'|',x.strip(),'|'
#替换字符
x = 'xyxxyy xin yyxx'
print '|',x.lstrip('xy'),'|',x.rstrip('xy'),'|',x.strip('xy'),'|'
'''
1.6 合并字符串
'''
#将一个字符串列表合并成一个字符串
pieces = ['a','b','c']
largeString = ''.join(pieces)
s1 = 'a'
s2 = 'b'
s3 = 'c'
lasgeString = '%s%s sasdf  dsafgasdfg asdf %s' % (s1, s2, s3)
#一些看似不错却效率低的做法
largeString = s1 + s2 + s3

for piece in pieces:
    largeString +=piece

import operator
largeString = reduce(operator.add, pieces, '')
#python中字符串对象是不可改变的，任何对字符串的操作，包括字符串的拼接都将产生一个新的字符串对象
#而不是修改原有的对象。因此拼接N个字符串将涉及创建并丢弃N-1个中间结果
'''
1.7 将字符串逐字符或逐词反转
'''
#字符串无法改变，所以，反转一个字符串需要创建一个拷贝。最简单的方法是使用一种步长为-1的切片方法
astring = 'abcdefg'
revchars = astring[::-1]
print astring
print revchars
#按照单词反转字符串。先创建一个单词列表，然后将列表反转，然后join合并，并且插入空格
astring = 'My name is xin'
revwords = astring.split()    #字符串->单词列表
revwords.reverse()            #反转列表
revwords = ' '.join(revwords) #单词列表->字符串
print revwords
#也可以这样写
revwords = ' '.join(astring.split()[::-1])
print revwords
##正则表达式
import re
revwords = re.split(r'(\s+)', astring)
revwords.reverse()
revwords = ' '.join(revwords)
#或者
revwords = ' '.join(re.split(r'(\s+)', astring)[::-1])
'''
1.8 检查字符串中是否包含某字符集合中的字符
'''
def containsAny(seq, aset):
    """检查序列seq是否含有aset中的项"""
    for c in seq:
        if c in aset: return True
    return False
#也可以使用更高级和更复杂的基于标准库itertools模块的方法来提高一点性能，不过他们本质上其实是同一种方法
import itertools
def containsAny1(seq, aset):
    for item in itertools.ifilter(aset.__contains__, seq):
        return True
    return False

'''
1.9 简化字符串的translate方法的使用
'''
import string
def translator(frm = '', to = '', delete = '', keep = None):
    if len(to) == 1:
        to = to * len(frm)
    trans = string.maketrans(frm, to)
    if keep is not None:
        allchars = string.maketrans('', '')
        delete = allchars.translate(allchars, keep.translate(allchars, delete))
    def translate(s):
        return s.translate(trans, delete)
    return translate

digits_only = translator(keep=string.digits)
print digits_only('Chris Perkins : 224-7992')
'''
1.10 过滤字符串中不属于指定集合的字符
'''
import string
#生成所有字符的可复用的字符串，它还可以作为一个翻译表，这里无需翻译
allchars = string.maketrans('','')
def makefilter(keep):
    """
    #返回一个函数，此返回函数接受一个字符串为参数，并返回字符串的一个部分拷贝
    #此拷贝只包含在keep中的字符，注意keep必须是一个普通字符串
    """
    #生成一个由所有不在keep中的字符组成的字符串：keep的补集，即所有我们需要删除的字符
    delchars = allchars.translate(allchars, keep)
    #生成并返回需要的过滤函数（作为闭包）
    def thefilter(s):
        return s.translate(allchars, delchars)
    return thefilter
just_vowels = makefilter('aeiouy')
print just_vowels('four score and seven yesrs ago')
'''
1.11 检查一个字符串是文本还是二进制
'''
#from _future_ import division  #确保/不会截断
import string
text_characters = "".join(map(chr, range(32, 127))) + "\n\r\t\b"
_null_trans = string.maketrans("", "")
def istext(s, text_characters = text_characters, threshold = 0.30):
    #若s包含了空值，它不是文本
    if "\0" in s :
        return False
    #一个“空”字符串是“文本”（这是一个主观但又很合理的选择）
    if not s:
        return True
    #获得s的由非文本字符构成的子串
    t = s.translate(_null_trans, text_characters)
    #如果不超过30%的字符是非文本字符，s是字符串
    return len(t)/len(s) <= threshold

'''
1.12 控制大小写
'''
#将一个字符串由大写转成小写，或者反其道而行之
#upper和lower方法，不需要参数，直接返回一个字符串的拷贝
little = "abc"
big = little.upper()
print big
big = "ABC"
little = big.lower()
print little
#s.capitalize和s[:1].upper()+s[:1].lower()相似，第一个字符被改成大写，其余字符被转成小写，s.title相似，不过将
#每个单词的第一个字母大写（这里的单词可以使字母的序列）
print 'one tWo thrEE'.capitalize()
print 'one tWo thrEE'.title()
#可以检查字符串是否已经满足需求的形式，比如isupper，islower，istitle，但是却没有iscapitalized
#iscapitalized函数实现
def iscapitalized(s):
    return s == s.capitalize()
#不过这偏离了“is...”方法们的行为模式，对于空字符串和不含字母的字符串，它也返回True，我们再给出一个严格点的版本
'''
#只适用于普通字符串，不适用于Unicode
import string
notrans = string.maketrans('','')
def containsAny1(str, strset):
    return len(strset) != len(strset.translate(notrans, str))
def iscapitalized1(s):
    return s == s.capitalize() and containsAny1(s, string.letters)
'''
'''
1.13 访问子字符串
'''
'''
1.14 改变多行文本字符串的缩进
'''
def reindent(s, numSpaces):
    leading_space = numSpaces * ' '
    lines = [ leading_space + line.strip() for line in s.splitlines()]
    return '\n'.join(lines)
x = """line one
    line two
        line three"""
print reindent(x, 4)
'''
1.15 扩展和压缩制表符
'''
#将字符串中的制表符转化成一定数目的空格，或者反其道而行之
mystring = "    ddd"
mystring = mystring.expandtabs(4)
print mystring
#这样并不会改变mystring原先指向的字符串对象，只不过将名字mystring绑定到了一个新创建的修改过的字符串拷贝上了。
#将空格替换成制表符
def unexpand(astring, tablen=8):
    import re
    #切分成空格和非空格的序列
    pieces = re.split(r'( +)', astring.expandtabs(tablen))
    #记录目前的字符串总长度
    lensofar = 0
    for i, piece in enumerate(pieces):
        thislen = len(piece)
        lensofar += thislen
        if piece.isspace():
            #将各个空格序列改成tabs + spaces
            numblanks = lensofar % tablen
            numtabs = (thislen - numblanks + tablen - 1)/tablen
            pieces[i] = '\t' * numtabs + ' '*numblanks
#return ''.join(pieces)
'''
1.16 替换字符串中的子串
'''
def expand(format, d, marker='"', safe=False):
    if safe:
        def lookup(w): return d.get(w, w.join(marker*2))
    else:
        def lookup(w): return d[w]
    parts = format.split(marker)
    parts[1::2] = map(lookup, parts[1::2])
    return ''.join(parts)
print expand('just "a" test', {'a':'one'})
'''
1.17 替换字符串中的子串——Python2.4
'''
#Python2.4提供了一个新的string.Template类，可以应用于这个任务
import string
#从字符串生成模板，其中标识符被$标记
new_style = string.Template('this is $thing')
#给模板的substitute方法传入一个字典参数并调用之
print new_style.substitute({'thing':5})#输出this is 5
print new_style.substitute({'thing':'test'})
print new_style.substitute(thing=5)
print new_style.substitute(thing='test')
#this is 5
#this is test
#this is 5
#this is test
'''
1.18 一次完成多个替换
'''
#re.escape(string)
#对字符串中的非字母数字进行转义
import re
def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)
'''
1.19 检查字符串中的结束标记
'''
import itertools
def anyTrue(predicate, sequence):
    return True in itertools.imap(predicate, sequence)

def endsWith(s, *endings):
    return anyTrue(s.endswith, endings)
#过滤图片
import os
for filename in os.listdir('.'):
    if endsWith(filename, '.jpg', '.jpeg', '.gif'):
        print filename
        
'''
1.20 使用Unicode来处理国际化文本
'''
german_ae = unicode('\xc3\xa4', 'utf8')
print german_ae
'''
1.21 在Unicode和普通字符串之间转换
'''
#需要处理一些可能不符合ASC字符集的文本数据
unicodestring = u"Hello world"
#将Unicode转化为普通Python字符串：“encode”
utf8string = unicodestring.encode("utf-8")
print utf8string
asciistring = unicodestring.encode("ascii")
print asciistring
#将普通python字符串转化为Unicode：“decode”
plainstring1 = unicode(utf8string, "utf-8")
print plainstring1
'''
1.22 在标准输出中打印Unicode字符
'''
import codecs, sys
sys.stdout = codecs.lookup('iso8859-1')[-1](sys.stdout)
'''
1.23 对Unicode数据编码并用于XML和HTML
'''
def encode_for_xml(unicode_data, encoding='ascii'):
    return unicode_data.encode(encoding, 'xmlcharrefreplace')
'''
1.24 让某些字符串大小写不敏感
'''
#想让某些字符串在比较和查询的时候是大小写不敏感的，但在其他操作中却保持原状
class iStr(str):
    """
    #大小写不敏感的字符串类
    #行为方式类似于str，只是所有的比较和查询都是大小写不敏感的
    """
    def __init__(self, *args):
        self._lowered = str.lower(self)
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__,str.__repr__(self))
    def __hash__(self):
        return hash(self._lowered)
    def lower(self):
        return self._lowered

def _make_case_insensitive(name):
    """将str的方法封装成iStr的方法，大小写不敏感"""
    str_meth = getattr(str, name)
    def x(self, other, *args):
        """
        #先尝试将other小写化，通常这应该是一个字符串
        #但必须要做好准备应对这个过程中出现的错误
        #因为字符串是可以和非字符串正确的比较的
        """
        try: other = other.lower()
        except (TypeError, AttributeError, ValueError): pass
        return str_meth(self._lowered, other, *args)
    setattr(iStr, name, x)
#将_make_case_insensitive函数应用于指定的方法
for name in 'eq lt le gt gt ne cmp contains'.split():
    _make_case_insensitive('__%s__' % name)
for name in 'count endswith find index rfind rindex startswith'.split():
    _make_case_insensitive(name)
del _make_case_insensitive