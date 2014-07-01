#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
# python cookbook 第六章 面向对象编程
# Writer：xin.change.the.world@gmail.com
# Date：2014-06-12
# github: https://github.com/xin-change-the-world/python-cookbook
#
'''
'''
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
'''
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
# 需要实现的是一个映射，在内部这个映射可以将任务按顺序委托给其他映射。
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

'''
6.5 继承的替代方案——自动托管
'''
# 你需要从某个类或者类型继承，但是需要对继承做一些调整。比如，需要选择性地隐藏某些基类的方法，而继承并不能做到这一点
# 继承是很方便，但它不是万用良药。比如，它无法让你隐藏基类的方法或者属性。而自动托管技术则提供了一种很好的选择。假设需要把一些对象封装起来变成只读对象，从而避免意外修改的情况。
# 那么，除了禁止属性设置的功能，还需要隐藏修改属性的方法。
# 同时支持2.3和2.4
try: set
except NameError: from sets import Set as set
class ROError(AttributeError): pass
class Readonly: # 这里并没有用继承，我们会在后面讨论其原因
    mutators = {
        list: set('''__delitem__ __delslice__ __iadd__ __imul__
                    __setitem__ __setslice__ append extend insert
                    pop remove sort'''.split()),
        dict: set('''__delitem__ __setitem__ clear pop popitem
                    setdefault update'''.split()),
        }
    def __init__(self, o):
        object.__setattr__(self, '_o', o)
        object.__setattr__(self, '_no', self.mutators.get(type(o), ()))
    def __setattr__(self, n, v):
        raise ROError, "Can't set attr %r on RO object" % n
    def __delattr__(self, n):
        raise ROError, "Can't del attr %r from RO object" % n
    def __getattr__(self, n):
        if n in self._no:
            raise ROError, "Can't get attr %r from RO object" % n
        return getattr(self._o, n)

# 不使用继承的原因：这种基于 __getattr__ 的方式也可用于特殊方法，但仅对旧风格类的实例有效。
# 在新的对象模型中，Python操作直接通过类的特殊方法来进行，而不是实例的。

'''
6.6 在代理中托管特殊方法
'''
print "----------------------------6.6在代理中托管特殊方法----------------------------"
# 在新风格对象模型中，Python操作其实是在类中查找特殊方法的（而不是在实例中，那是经典对象模型的处理方式）
# 现在，需要将一些新风格的实例包装到代理类中，此代理可以选择将一些特殊方法委托给内部的被包装对象
# 你需要即时地生成各个代理类
class Proxy(object):
    """ 所有代理的基类 """
    def __init__(self, obj):
        #super(Proxy, self).__init__(obj)
        super(Proxy, self).__init__()
        self._obj = obj
    def __getattr__(self, attrib):
        return getattr(self._obj, attrib)
def make_binder(unbound_method):
    def f(self, *a, **k): return unbound_method(self._obj, *a, **k)
    # 仅2.4：f.__name__ = unbound_method.__name__
    return f
known_proxy_classes = {}
def proxy(obj, *specials):
    ''' 能够委托特殊方法的代理的工厂函数 '''
    # 我们手上有合适的自定义的类吗？
    obj_cls = obj.__class__
    key = obj_cls, specials
    cls = known_proxy_classes.get(key)
    if cls is None:
        # 我们手上没有合适的类，那就现做一个
        cls = type("%sProxy" % obj_cls.__name__, (Proxy,), {})
        for name in specials:
            name = '__%s__' % name
            unbound_method = getattr(obj_cls, name)
            setattr(cls, name, make_binder(unbound_method))
        # 缓存之以供进一步使用
        known_proxy_classes[key] = cls
    # 实例化并返回需要的代理
    return cls(obj)
a = proxy([ ], 'len', 'iter') # 只托管len和iter
print a
print a.__class__
print a._obj
print a.append # 所有非特殊方法都被托管了
print len(a)
a.append(23)
print len(a)
# 由于__iter__被托管了，for循环也如同预期那样工作
for x in a:
    print x
print list(a)
print sum(a)
print max(a)
# 不过由于__getitem__没有被托管，a无法进行索引或切片操作：
#print a.__getitem__
#print a[1]
'''
  File "C:\Users\guangxin\Documents\GitHub\python-cookbook\python-cookbook\cook_6.py", line 316, in <module>
    print a[1]
TypeError: 'listProxy' object does not support indexing
'''
'''
6.7 有命名子项的元组
'''
# Python元组可以很方便地被用来将信息分组，但是访问每个子项都需要使用数字索引，所以这种用法有点不便。
# 你希望能够创建一种可以通过名字属性访问的元组
# 工厂函数是生成符合要求的元组的子类的最简单方法：
# 若在2.4中可以使用operator.itemgetter,若在2.3中则需要实现itemgetter
'''
operator.itemgetter函数
operator模块提供的itemgetter函数用于获取对象的哪些维的数据，参数为一些序号（即需要获取的数据在对象中的序号），下面看例子。
a = [1,2,3] 
>>> b=operator.itemgetter(1)      //定义函数b，获取对象的第1个域的值
>>> b(a) 
2 
>>> b=operator.itemgetter(1,0)   //定义函数b，获取对象的第1个域和第0个的值
>>> b(a) 
(2, 1) 
要注意，operator.itemgetter函数获取的不是值，而是定义了一个函数，通过该函数作用到对象上才能获取值。
'''
try:
    from operator import itemgetter
except importError:
    def itemgetter(i):
        def getter(self): return self[i]
        return getter
def superTuple(typename, *attribute_names):
    ''' 创建并返回拥有名字属性的元组子类 '''
    # 给子类适合的__new__和__repr__特殊方法
    nargs = len(attribute_names)
    class supertup(tuple):
        #python新模式的class，即从object继承下来的类有一个变量是__slots__，slots的作用是阻止在实例化类时为实例分配dict，默认情况下每个类都会有一个dict,通过__dict__访问，这个dict维护了这个实例的所有属性
        __slots__ = ()     # 我们不需要每个实例提供一个字典，节省内存
        def __new__(cls, *args):
            if len(args) != nargs:
                raise TypeError, '%s takes exactly %d arguments (%d given)' % (typename, nargs, len(args))
            return tuple.__new__(cls, args)
        def __repr__(self):
            return '%s(%s)' % (typename, ', '.join(map(repr, self)))
    # 给我们的元组子类添加一些键
    for index, attr_name in enumerate(attribute_names):
        setattr(supertup, attr_name, property(itemgetter(index)))
    supertup.__name__ = typename
    return supertup

Point = superTuple('Point', 'x', 'y')
print Point
#p = Point(1, 2, 3) # 故意给错误的数字
#print p
p = Point(1, 2)
print p
print p.x, p.y

'''
6.8 避免属性读写的冗余代码
'''
# 你的类会用到property实例，而getter或者setter都是一些千篇一律的获取或者设置实例属性的代码。你希望只用指定属性名，而不用写那些非常相似的代码。
# 需要一个工厂函数，用它来处理那些getter或setter的参数是字符串的情况，并将正确的参数封装到一个函数中，然后将其余的工作委托给Python内建的property
def xproperty(fget, fset, fdel=None, doc=None):
    if isinstance(fget, str):
        attr_name = fget
        def fget(obj): return getattr(obj, attr_name)
    elif isinstance(fset, str):
        attr_name = fset
        def fset(obj, val): setattr(obj, attr_name, val)
    else:
        raise TypeError, 'either fget or fset must be a str'
    return property(fget, fset, fdel, doc)
# 当你需要一个setter和一个getter时，其中的一个需要执行一些额外的代码；而另一个则只需要简单地读取或者写入实例的属性。
# 此时，property需要两个函数作为它的参数。其中的一个函数就是所谓的“样板代码”
class Lower(object):
    def __init__(self, s=''):
        self.s = s
    def _getS(self):
        return self,_s
    def _setS(self, s):
        self._s = s.lower()
    s = property(_getS, _setS)
# _getS就是样板代码，但你仍需要编写这些代码，因为你要将它传递给property
# 使用本节的方案，可以让你的代码变得更简洁，同时丝毫不改变愿意：
class Lower(object):
    def __init__(self, s=''):
        self.s = s
    def _setS(self, s):
        self._s = s.lower()
    s = xproperty('_s', _setS)

'''
6.9 快速复制对象
'''
# 为了使用copy.copy，需要实现特殊方法__copy__。而且你的类的__init__比较耗时，
# 所以你希望能够绕过它并获得一个“空的”未初始化的类实例
# 下面的解决方案可同时适用于新风格和经典类
def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    newcopy = Empty()
    newcopy.__class__ = obj.__class__
    return newcopy
# 你的类可以使用这个函数来实现__copy__
class YourClass(object):
    def __init__(self):
        print "assume there's a lot of work here"
    def __copy__(self):
        newcopy = empty_copy(self)
        return newcopy

y = YourClass()  # 很显然__init__会被调用
print y
z = copy.copy(y) # 不调用__init__
print z
# 下面两种复制所有属性的方式都是可行的：
#newcopy.__dict__.update(self.__dict__)
#newcopy.__dict__ = dict(self.__dict__)

'''
6.10 保留对被绑定方法的引用且支持垃圾回收
'''
print "================6.10 保留对被绑定方法的引用且支持垃圾回收=============="
# 你想保存一些指向被绑定方法的引用，同时还需要让关联的对象可以被垃圾收集机制处理
# 弱引用（弱引用在一个对象处于生存周期时指向该对象，但如果没有其他正常的引用指向该对象时，这个对象不会被保留）
# Python标准库的weakref模块允许我们使用弱引用
import weakref, new
class ref(object):
    """
    # 能够封装任何可调用体，特别是被绑定方法，而且被绑定方法仍然能被回收处理。与此同时，提供一个普通的弱引用的接口
    """
    def __init__(self, fn):
        try:
            # 试图获得对象、函数和类
            o, f, c = fn.im_self, fn.im_func, fn.im_class
        except AttributeError:       # 非被绑定方法
            self._obj = None
            self._func = fn
            self._clas = None 
        else:                        # 绑定方法
            if o is None: self._obj = None       # 实际上没绑定
            else: self._obj = weakref.ref(o)         # 确实绑定了
            self._func = f
            self._clas = c
    def __call__(self):
        if self.obj is None: return self._func
        elif self._obj() is None: return None 
        return new.instancemethod(self._func, self.obj(), self._clas)

# 一个正常的被绑定方法拥有一个指向此方法所属对象的强引用。
# 这意味着除非这个被绑定方法被消灭掉，否则该对象不能被当做垃圾重新回收。
class C(object):
    def f(self):
        print "Hello"
    def __del__(self):
        print "C dying"

c = C()
cf = c.f
del c   # c眨巴眨巴眼睛活的好好的
del cf  # 直到我们干掉了被绑定的方法，它才终于安心地去了

'''
6.11 缓存环的实现
'''
# 你想定义一个固定尺寸的缓存，当它被填满时，新加入的元素会覆盖第一个(最老的)元素。
# 这种数据结构在存储日志和历史信息时非常有用
class RingBuffer(object):
    """ 这是一个未填满的缓存类 """
    def __init__(self, size_max):
        self.max = size_max
        self.data = []
    class __Full(object):
        """ 这是一个填满了的缓存类 """
        def append(self, x):
            """ 加入新的元素覆盖最旧的元素 """
            self.data[self.cur] = x
            self.cur = (self.cur + 1) % self.max
        def tolist(self):
            """ 以正确的顺序返回元素列表 """
            return self.data[self.cur:] + self.data[:self.cur]
    def append(self, x):
        """ 在缓存末尾增加一个元素 """
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # 永久性地将self的类从非满改成满
            self.__class__ = self.__Full
    def tolist(self):
        """ 返回一个从最旧的到最新的元素的列表 """
        return self.data
#用法示例
x = RingBuffer(5)
x.append(1); x.append(2); x.append(3); x.append(4); 
print x.__class__, x.tolist()
x.append(5)
print x.__class__, x.tolist()
x.append(6)
print x.data, x.tolist()
x.append(7); x.append(8); x.append(9); x.append(10); 
print x.data, x.tolist()

# 另一种选择是，我们可以切换实例的两个方法而非整个类，来使它变成填满的状态
class RingBuffer(object):
    def __init__(self, size_max):
        self.max = size_max
        self.data = []
    def _full_append(self, x):
        self.data[self.cur] = x
        self.cur = (self.cur + 1) % self.max
    def _full_get(self):
        return self.data[self.cur:] + self.data[:self.cur]
    def append(self, x):
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            self.append = self._full_append
            self.tolist = self._full_get
    def tolist(self):
        return self.data

'''
6.12 检查一个实例的状态变化
'''
# 一个实例在上次“保存”操作之后又被修改了，需要检查它的状态变化以便有选择地保存此实例。
# 一个有效的方案是mixin类，这个类可以从多个类继承并能对一个实例的状态进行快照操作，这样就可以用此实例的当前状态和上次的快照做比较，来判断它是否被修改过了
import copy
class ChangeCheckerMixin(object):
    containerItems = {dict: dict.iteritems, list:enumerate}
    immutable = False
    def snapshot(self):
        """
        # 创建self状态的“快照”——就像浅拷贝，但只对容器的类型递归
        # 而不是整个实例，在需要时实例会自行记录自己的状态变化
        """
        if self.immutable:
            return 
        self._snapshot = self._copy_container(self.__dict__)
    def makeImmutable(self):
        ''' 实例状态无法被修改，设置.immutable '''
        self.immutable = True
        try:
            del self._snapshot
        except AttributeError:
            pass
    def _copy_container(self, container):
        ''' 半浅拷贝，只对容器类型递归 ''' 
        new_container = copy.copy(container)
        for k, v in self.containerItems[type(new_container)](new_container):
            if type(v) in self.containerItems:
                new_container[k] = self._copy_container(v)
            elif hasattr(v, 'snapshot'):
                v.snapshot()
        return new_container
    def isChanged(self):
        ''' 从上次快照之后如果有变化返回True '''
        if self.immutable:
            return False
        # 从self.__dict__中删除快照，并置之于末尾
        snap = self.__dict__.pop('_snapshot', None)
        if snap is None:
            return True
        try:
            return self._checkContainer(self.__dict__, snap)
        finally:
            self._snapshot = snap
    def _checkContainer(self, container, snapshot):
        ''' 如果容器和快照不同，返回True '''
        if len(container) != len(snapshot):
            return True
        for k, v in self.containerItems[type(container)](container):
            try:
                ov = snapshot[k]
            except LookupError:
                return True
            if self._checkItem(v, ov):
                return True
        return False
    def _checkItem(self, newitem, olditem):
        ''' 
        # 比较新旧元素，如果他们是容器类型，递归调用
        # self._checkContainer recursivly.如果他们是带有“isChanged”
        # 方法的实例，则委托给该方法，如果两者不相同，则返回True
        '''
        if type(newitem) != type(olditem):
            return True
        if type(newitem) in self.containerItems:
            return self._checkContainer(newitem, olditem)
        if newitem is olditem:
            method_isChanged = getattr(newitem, 'isChanged', None)
            if method_isChanged is None:
                return False
            return method_isChanged()
        return newitem != olditem

'''
6.13 检查一个对象是否包含某种必要的属性
'''
# 你想在进行状态修改操作之前检查一个对象是否有某种必要的属性，但你想避免使用类型检查的方式，因为那样会打破多态机制的灵活性
def munge4(alist):
    # 首先得到所有需要的被绑定方法（迅速获取异常而且不会造成部分修改现象，如果需要的方法不存在的话）
    append = alist.append
    extend = alist.extend
    # 检查索引之类的操作以便尽快地获得异常
    # 如果不满足签名兼容性的话
    try: alist[0] = alist[0]
    except IndexError: pass  # 空的alist也没问题
    # 开始操作：这之后不会再有异常发生了
    append(23)
    extend(range(5))
    alist[4] = alist[3]
    extend(range(2))

'''
6.14 实现状态设计模式
'''
# 你希望你程序中的某个对象能在不同的“状态”之间切换，而且该对象的行为方式也能随着状态的变化而变化
# 状态设计模式的关键思路是将“状态”（带有它自身的行为方式）对象化，使其成为一个类实例（带有一些方法）
# 在Python中，你不用创建一个抽象类来表现这些不同状态共同的接口：只需为这些“状态”本身编写不同的类即可。
class TraceNormal(object):
    """ 正常的状态 """
    def startMessage(self):
        self.nstr = self.characters = 0
    def emitString(self, s):
        self.nstr += 1
    def endMessage(self):
        print '%d characters in %d strings' % (self.characters, self.nstr)
class TraceChatty(object):
    """ 详细的状态 """
    def startMessage(self):
        self.msg = []
    def emitString(self, s):
        self.msg.append(repr(s))
    def endMessage(self):
        print 'Message: ', ', '.join(self.msg)
class TraceQuiet(object):
    """ 输出的状态 """
    def startMessage(self): pass
    def emitString(self, s): pass
    def endMessage(self): pass
class Tracer(object):
    def __init__(self, state): self.state = state
    def setState(self, state): self.state = state
    def emitStrings(self, strings):
        self.state.startMessage()
        for s in strings: self.state.emitStrings(s)
        self.state.endMessage()
t = Tracer(TraceNormal())
t.emitStrings('some example strings here'.split())
t.setState(TraceQuiet())
t.emitStrings('some example strings here'.split())
t.setState(TraceChatty())
t.emitStrings('some example strings here'.split())

'''
6.15 实现单例模式
'''
# 你想保证某个类从始至终最多只能有一个实例
# __new__静态方法使得这个任务极其简单
class Singleton(object):
    """ 一个Python风格的单例模式 """
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst
# 然后只需从Singleton派生子类即可，而且不需要重载__new__
# 然后所有对此类的调用（通常是创建新实例）都将返回一个实例
class SingleSpam(Singleton):
    def __init__(self, s): self.s = s
    def __str__(self): return self.s
s1 = SingleSpam('spam')
print id(s1), s1.spam()
s2 = SingleSpam('eggs')
print id(s2), s2.spam()

'''
6.16 用Borg管用来避免“单例”模式
'''
# 你想保证某个类从始至终最多只能有一个实例：你并不关心生成的实例的id，只关心其状态和行为方式，而且你还想确保它具有子类话能力
# 允许多个实例被创建，但所有实例都共享状态和行为方式。
class Borg(object):
    _shared_state = {}
    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj
class Example(Borg):
    name = None 
    def __init__(self, name=None):
        if name is not None: self.name = name
    def __str__(self): return 'name->%s' % self.name
a = Example('Lara')
b = Example()
print a, b
c = Example('John Malkovich')
print a, b, c
b.name = "Seven"
print a, b, c

'''
6.17 Null对象设计模式的实现
'''
# 你想减少代码中条件声明，尤其是针对特殊情况的检查
# 一种常见的代表“这里什么也没有”的占位符是None，但我们还可以定义一个类，其行为方式和这种占位符相似，而且效果更好
class Null(object):
    """ Null对象总是很可靠地什么也不做 """
    # 可选的优化：确保每个子类只有一个实例
    # 完全是为了节省内存，功能上没有任何差异
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = type.__new__(cls, *args, **kwargs)
        return cls._inst
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __repr__(self): return "Null()"
    def __nonzero__(self): return False
    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return self
    def __delattr__(self, name): return self

# 示例
log = err = Null()
if verbose:
    log = open('/tmp/log','w')
    err = open('/tmp/err','w')
log.write('blabla')
err.write('blabla err')

'''
6.18 用__init__参数自动初始化实例变量
'''
# 你想避免编写和维护一种烦人的几乎什么也不做的__init__方法，这种方法中含有一大堆形如self.something=something的赋值语句
# 可以把那些属性赋值任务抽取出来置入一个辅助函数中：
def attributesFromDict(d):
    self = d.pop('self')
    for n, v in d.iteritems():
        setattr(self, n, v)
# 而__init__方法里的那种千篇一律的赋值语句大概是这个样子的：
'''
def __init__(self, foo, bar, baz, boom=1, bang=2):
    self.foo = foo
    self.bar = bar
    self.baz = baz
    self.boom = boom
    self.bang = bang
# 现在可以i被缩减为清晰的一行
def __init__(self, foo, bar, baz, boom=1, bang=2):
    attributesFromDict(locals())
# 一个相似但更简单的技术是，不适用辅助函数，而是像下面这样：
def __init__(self, foo, bar, baz, boom=1, bang=2):
    self.__dict__.update(locals())
    del self.self
# 不过这种技术对于一些特性和高级描述符，它无法正常工作，setattr在这方面表现得很完美
'''

'''
6.19 调用超类的__init__方法
'''
# 你想确保所有的超类的__init__方法被自动调用（如果该超类定义过__init__方法），但Python并不会自动调用此方法
# 如果你的类是新风格类，内建的super会使这个任务变得极其简单（如果所有的超类的__init__方法也用相似的方式使用super）
class NewStyleOnly(A, B, C):
    def __init__(self):
        super(NewStyleOnly, self).__init__()
# 如果你确实无法完成准备工作，那么你能做的就是循环检查基类——对于每个基类，都看它是否拥有__init__。如果有的话，调用该方法：
class LookBeforeYouLeap(X, Y, Z):
    def __init__(self):
        for base in self.__class__.__bases__:
            if hasattr(base, '__init__'):
                base.__init__(self)

'''
6.20 精确和安全滴使用协作的超类调用
'''
# 你很欣赏通过内建的super来支持的多继承的代码的协作方式，但同时你也希望能够更加简洁和精确地使用这种方式
# 一个好的方案是使用支持多继承的mixin类，此类使用了内省机制，且更加简洁：
import inspect
class SuperMixin(object):
    def super(cls, *args, **kwargs):
        frame = inspect.currentframe(1)
        self = frame.f_locals['self']
        methodName = frame.f_code.co_name
        method = getattr(super(cls, self), methodName, None)
        if inspect.ismethod(method):
            return method(*args, **kwargs)
    super = classmethod(super)

class TestBase(list, SuperMixin):
    # 注意：myMethod并未在此定义
    pass
class MyTest1(TestBase):
    def myMethod(self):
        print "in MyTest1"
        MyTest1.super()
class MyTest2(TestBase):
    def myMethod(self):
        print "in MyTest2"
        MyTest2.super()
class MyTest(MyTest1, MyTest2):
    def myMethod(self):
        print "in MyTest"
        MyTest.super()
MyTest().myMethod()