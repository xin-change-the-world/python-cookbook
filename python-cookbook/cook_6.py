#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第六章 面向对象编程
# Writer：张广欣
# Date：2014-06-12
#
#
'''
"""
6.1　温标的转换 223
6.2　定义常量 225
6.3　限制属性的设置 227
6.4　链式字典查询 229
6.5　继承的替代方案-自动托管 231
6.6　在代理中托管特殊方法 234
6.7　有命名子项的元组 237
6.8　避免属性读写的冗余代码 239
6.9　快速复制对象 240
6.10　保留对被绑定方法的引用且支持垃圾回收 243
6.11　缓存环的实现 245
6.12　检查一个实例的状态变化 249
6.13　检查一个对象是否包含某种必要的属性 252
6.14　实现状态设计模式 255
6.15　实现单例模式 257
6.16　用Borg惯用法来避免"单例"模式 259
6.17　Null对象设计模式的实现 263
6.18　用_ _init_ _参数自动初始化实例变量 266
6.19　调用超类的_ _init_ _方法 267
6.20　精确和安全地使用协作的超类调用 270
"""
'''
#在python中最好的方式是使用模块，而不是一个OOP对象
'''
'''
6.1 温标的转换
'''
#你想在开式温度（Kelvin）、摄氏度（Celsius）、华氏温度（Fahrenheit）以及兰金（Rankine）温度之间做转换
class Temperature(object):
    coefficients = {'c':(1.0, 0.0, -273.15), 
                    'f':(1.8, -273.15, 32.0), 
                    'r':(1.8, 0.0, 0.0)}
    def __init__(self, **kwargs):
        #默认是绝对（开式）温度0，但可接受一个命名的参数
        #名字可以是k、c、f或r，分别对应不同的温标
        try:
            name, value = kwargs.popitem()
        except KeyError:
            #无参数 默认k=0
            name, value = 'k', 0
        #若参数过多或参数不能识别，报错
        if kwargs or name not in 'kcfr':
            kwargs[name] = value #将其置回，做诊断用
            raise TypeError, 'invalid arguments %r' % kwargs
        setattr(self, name, float(value))
    def __getattr__(self, name):
        #将c、f、r的获取映射到k的计算
        try:
            eq = self.coefficients[name]
        except KeyError:
            #未知名字，提示错误
            raise AttributeError, name
    def __setattr__(self, name, value):
        #将对k，c，f，r的设置映射到对k的设置；并禁止其他的选项
        if name in self.coefficients:
            #名字是c、f或r——计算并设置k
            eq = self.coefficients[name]
            self.k = (value - eq[2]) / eq[0] - eq[1]
        elif name == 'k':
            #名字是k，设置之
            object.__setattr__(self, name, value)
        else:
            #未知名，给出错误信息
            raise AttributeError, name
    def __str__(self):
        #以易读和简洁的格式打印
        return "%s K" % self.k
    def __repr__(self):
        #以详细和准确的格式打印
        return "Temperature(k=%r)" % self.k

#假设你将以上代码存为te.py，并置入你的Python的sys.path就可以将它作为模块引入
#from te import Temperature
t = Temperature(f=70)
#print dir(t)
#print t.c
'''
6.2 定义常量
'''
#你需要定义一些模块级别的变量（比如命名的常量），而且客户代码无法将其重新绑定
#你可以把任何对象当做模块一样安装。将下列代码存为一个模块const.py，并放入你的Python的sys.path指定的目录中

class _const(object):
	class ConstError(TypeError): pass
	def __setattr__(self, name, value):
		if name in self.__dict__:
			raise self.ConstError, "Can't rebind const(%s)" % name
		self.__dict__[name] = value
	def __delattr__(self, name):
		if name in self.__dict__:
			raise self.ConstError, "Can't unbind const(%s)" % name
		raise NameError, name
import sys
sys.modules[__name__] = _const()


''' 示例 '''
'''
import const

#现在任何客户端代码都可以导入const，并将const模块的一个属性绑定一次，但仅能绑定一次
const.magic = 23
print const.magic
#一旦某属性已经被绑定，程序无法将其重新绑定或者解除绑定：
try:
    const.magic = 88 #抛出const.ConstError
    del const.magic  #抛出const.ConstError
except:
    print "ConstError"
'''
'''
6.3 限制属性的设置
'''
#通常情况下，Python允许随意给类和类实例增加属性。但对于某些特定的类，你却希望这种自由受到限制。
#特殊方法__setattr__会解读对属性的设置操作，它让你有机会限制新属性的添加。
#一个优雅的实现方法是写一个类和一个简单的自定义元类，再加上一个封装函数，像下面这样：
def no_new_attributes(wrapped_setattr):
    """
    #试图添加新属性时，报错，但允许已经存在的属性被随意设置
    """
    def __setattr__(self, name, value):
        if hasattr(self, name):#非新属性，允许
            wrapped_setattr(self, name, value)
        else: #新属性，禁止
            raise AttributeError("can't add attribute %r to %s" % (name, self))
    return __setattr__

class NoNewAttrs(object):
    """
    #NoNewAttrs的子类会拒绝新属性的添加，但允许已存在的属性被赋予新值
    """
    #向此类的实例添加新属性的操作被屏蔽
    __setattr__ = no_new_attributes(object.__setattr__)
    class __metaclass__(type):
        """ 一个简单的自定义元类，禁止向类添加新属性 """
        __setattr__ = no_new_attributes(type.__setattr__)

class Person(NoNewAttrs):
    firstname = ''
    lastname = ''
    def __init__(self, firstname, lastname):
        self.firstname = firstname
        self.lastname = lastname
    def __repr__(self):
        return 'Person(%r, %r)' % (self.firstname, self.lastname)
me = Person("Michere", "Simionato")
print me
me.firstname = "Michele"
print me
try:
    Person.address = ''
except AttributeError, err:
    print "raised %r as expected " % err

try:
    me.address = ''
except AttributeError, err:
    print "raised %r as expected " % err

'''
6.4 链式字典查询
'''
＃需要实现的是一个映射，在内部这个映射可以将任务按顺序委托给其他映射。
class Chainmap(object):
    def __init__(self, *mappings):
        # 记录映射的序列
        self._mappings = mappings
    def __getitem__(self, key):
        # 在序列的字典中查询
        for mapping in self._mappings:
            try:
                return mapping[key]
            except KeyError:
                pass
        # 没有在任何字典中找到key，所以抛出KeyError异常
        raise KeyError, key
    def get(self, key, default=None):
        # 若self[key]存在则返回之，否则返回default
        try:
            return self[key]
        except KeyError:
            return default
    def __contains__(self, key):
        # 若key在self中返回True,否则返回False
        try:
            self[key]
            return True
        except KeyError:
            return False

# 举个栗子，你现在就可以实现Python中用来查询名字的机制：先在局部变量中查找，然后（如果没有找到）再到全局变量中查找，
# 最后（如果还没有找到）到内置量中查找：
import __builtin__
pylookup = Chainmap(locals(), globals(), vars(__builtin__))

# 即使只读是我们设计上的选择，它也不是一个“完全的映射”。你可以通过继承DictMixin类
# 在标准库的UserDict模块中，并提供少量的关键方法（DictMixin实现了其他的方法）
# 将一个部分映射改变成“完全映射”。
import UserDict
from sets import Set
class FullChainmap(Chainmap, UserDict.DictMixin):
    def copy(self):
        return self.__class__(self._mappings)
    def __iter__(self):
        seen = Set()
        for mapping in self._mappings:
            for key in mapping:
                if key not in seen:
                    yield key
                    seen.add(key)
    iterkeys = __iter__
    def keys(self):
        return list(self)

# 除了Chainmap的对映射的要求，FullChainmap类又对封装的映射增加了一项要求：
# 映射必须是可迭代的。




























