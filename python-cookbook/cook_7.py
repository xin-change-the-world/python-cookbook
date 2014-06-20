#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第七章 持久化和数据库 
# Writer：xin.change.the.world@gmail.com
# Date：2014-06-18
# github: https://github.com/xin-change-the-world/python-cookbook
#
'''
"""
7.1　使用marshal模块序列化数据 275
7.2　使用pickle和cPickle模块序列化数据 277
7.3　在Pickling的时候压缩 280
7.4　对类和实例使用cPickle模块 281
7.5　Pickling被绑定方法 284
7.6　Pickling代码对象 286
7.7　通过shelve修改对象 288
7.8　使用Berkeley DB数据库 291
7.9　访问MySQL数据库 294
7.10　在MySQL数据库中储存BLOB 295
7.11　在PostgreSQL中储存BLOB 296
7.12　在SQLite中储存BLOB 298
7.13　生成一个字典将字段名映射为列号 300
7.14　利用dtuple实现对查询结果的灵活访问 302
7.15　打印数据库游标的内容 304
7.16　适用于各种DB API模块的单参数传递风格 306
7.17　通过ADO使用Microsoft Jet 308
7.18　从Jython Servlet访问JDBC数据库 310
7.19　通过Jython和ODBC获得Excel数据 313
"""
'''
7.1 使用marshal模块序列化数据 275
'''
# 你想以尽量快的速度来序列化并重新构造那些由基本Python对象（比如列表、元组、数字和字符串，但不包括类、类实例等）构成的数据结构
data = {12:'tweleve', 'feep':list('ciao'), 1.23:4+5j, (1,2,3):u'wer'}
# 可以以很快的速度将data转化为字节串
import marshal
bytes = marshal.dumps(data)
print bytes
redata = marshal.loads(bytes)
print redata
ouf = open('datafile.dat', 'wb')
marshal.dump(data, ouf)
marshal.dump('some string', ouf)
marshal.dump(range(19), ouf)
ouf.close()
# 以后还可以以固定的顺序从datafile.dat文件中回复出所有的数据结构
inf = open('datafile.dat', 'rb')
a = marshal.load(inf)
b = marshal.load(inf)
c = marshal.load(inf)
inf.close()
print a, b, c
# dump和load只能在同一个Python发行版本下正常工作
# marshal 不 保证在不同Python发行版之间的兼容性
'''
7.2 使用pickle和cPickle模块序列化数据
'''
# 你想以某种可以接受的速度序列化和重建Python数据结构，这些数据既包括基本Python对象也包括类和实例
data = {12:'tweleve', 'feep':list('ciao'), 1.23:4+5j, (1,2,3):u'wer'}
import cPickle
text = cPickle.dumps(data)
bytes = cPickle.dumps(data, 2)
redata1 = cPickle.loads(text)
redata2 = cPickle.loads(bytes)
# 字典的键在原数据和新建数据中的顺序都是任意的
ouf = open('datafile.txt', 'w')
cPickle.dump(data, ouf)
cPickle.dump('some string', ouf)
cPickle.dump(range(19), ouf)
ouf.close()

inf = open('datafile.txt')
a = cPickle.load(inf)
b = cPickle.load(inf)
c = cPickle.load(inf)
inf.close()

# cPickle保证了在不同Python发行版之间的兼容性

'''
7.3 在Pickling的时候压缩
'''
# 你想以一种压缩的方式来pickle一般的Python对象
# 标准库模块cPickle和gzip提供了所需的功能，你只需以适当的方式将他们粘合起来
import cPickle, gzip
def save(filename, *objects):
    ''' 将对象存为压缩过的磁盘文件 '''
    fil = gzip.open(filename, 'wb')
    for obj in objects: cPickle.dump(obj, fil, proto = 2)
    fil.close()
def load(filename):
    ''' 从压缩的磁盘文件中载入对象 '''
    fil = gzip.open(filename, 'rb')
    while True:
        try: yield cPickle.load(fil)
        except EOFError: break
    fil.close()

'''
7.4 对类和实例使用cPickle模块
'''
# 你想通过cPickle模块来存取类和实例对象
class PrettyClever(object):
    def __init__(self, *stuff):
        self.stuff = stuff
    def __getstate__(self):
        def normalize(x):
            if isinstance(x, file):
                return 1, (x.name, x.mode, x.tell())
            return 0, x
        return [ normalize(x) for x in self.stuff ]
    def __setstate__(self, stuff):
        def reconstruct(x):
            if x[0] == 0:
                return x[1]
            name, mode, offs = x[1]
            openfile = open(name, mode)
            openfile.seek(offs)
            return openfile
        self.stuff = tuple([reconstruct(x) for x in stuff])

'''
7.5 Pickling被绑定方法
'''
# 需要pickle一个对象，但是该对象持有（作为属性或子项）另一个对象的被绑定方法，而被绑定方法是无法被pickle处理的
import cPickle
class Greeter(object):
    def __init__(self, name):
        self.name = name
    def greet(self):
        print 'hello', self.name
class Repeater(object):
    def __init__(self, greeter):
        self.greeter = greeter
    def greet(self):
        self.greeter()
        self.greeter()
r = Repeater(Greeter('world').greet)
# 如果不是因为r持有了一个被绑定方法作为它的greeter属性，你本来可以很简单的实现对r的pickel处理：
# s = cPickle.dumps(r)
# 一个简单的解决办法是让Repeater类的每个实例都不直接持有被绑定方法，而是持有一个可以被pickle处理的对该方法的封装
class picklable_boundmethod(object):
    def __init__(self, mt):
        self.mt = mt
    def __getstate__(self):
        return self.mt.im_self, self.mt.im_func.__name__
    def __setstate__(self, (s, fn)):
        self.mt = getattr(s, fn)
    def __call__(self, *a, **kw):
        return self.mt(*a, **kw)
# 现在将Repeater.__init__的主体改成self.greeter=picklable_boundmethod(greeter)
# 就可以保证以前的代码片段正常工作

'''
7.6 Pickling代码对象
'''
# 你想对代码对象进行pickling处理，但标准库的pickle模块并不支持这个功能
# 可以通过使用copy_reg模块来扩展pickle模块的能力。
import new, types, copy_reg
def code_ctor(*args):
    # 委托给new.code，构造一个新的代码对象
    return new.code(*args)
def reduce_code(co):
    # 还原函数必须返回一个带两个子项的元组：第一个是在反序列化初期被用来构建参数对象的构造函数，
    # 第二个则是参数的元组，将被传递给构造函数作为参数
    if co.co_freevars or co.co_cellvars:
        raise ValueError,"Sorry, cannot pickle code objects from closures"
    return code_ctor, (co.co_argcount, co.co_nlocals, co.co_stacksize,
            co.co_flags, co.co_code, co.co_consts, co.co_names,
            co.co_varnames, co.co_filename, co.co_name, co.co_firstlineno, co.co_lnotab)
# 注册reductor用于pickle“CodeType类型的对象”
copy_reg.pickle(types.CodeType, reduce_code)
# pickle 代码对象用法示例
import cPickle
def f(x):print 'Hello,', x
# 将此函数的代码对象序列化为字节串
pickled_code = cPickle.dumps(f.func_code)
# 从字节串回复一个相等地代码对象
recovered_code = cPickle.loads(pickled_code)
# 用重建的代码对象创建一个新函数
g = new.function(recovered_code, globals())
# 看看调用新函数的效果
g('world')

'''
7.7 通过shelve修改对象
'''
import shelve
# 创建一个简单的例子shelf
she = shelve.open('try.she', 'c')
for c in 'spam': she[c] = {c:23}
for c in she.keys(): print c, she[c]
she.close()
she = shelve.open('try.she', 'c')
print she['p']
she['p']['p'] = 42
print she['p']
# 结果没有改变，问题在于我们处理的其实是shelve给我们的一个临时对象而已，而不是真家伙。
# 我们给临时对象绑定一个名字，然后完成我们的修改
a = she['p']
a['p'] = 42
she['p'] = a
print she['p']
she.close()
# 我们可以验证这个修改是否持久
she=shelve.open('try.she','c')
for c in she.keys(): print c, she[c]
she.close()
# 一个更简单的方法是将writeback选项设置为True，然后打开shelve对象
# she = shelve.open('try.she', 'c', writeback=True)
# 打开writeback选项后，shelve会跟踪所有从文件生成的对象，并在关闭之前将所有项回写到文件，这是因为在这个过程中他们可能被修改过
# 虽然代码简化了不少，但代价是高昂的，尤其是内存的消耗增加了很多。

'''
7.8 使用Berkeley DB数据库
'''
'''
7.9 访问MySQL数据库
'''
import MySQLdb
# 创建一个连接对象，再用它创建游标
con = MySQLdb.connect(host="127.0.0.1", port=3306, user="root", passwd="", db="test")
cursor = con.cursor()
# 执行一个SQL字符串
sql = "SELECT * FROM test;"
cursor.execute(sql)
# 从游标中取出所有记录放入一个序列并关闭连接
results = cursor.fetchall()
con.close()
print results

'''
7.10 在MySQL数据库中储存BLOB
'''
import MySQLdb, cPickle
connection = MySQLdb.connect(host="127.0.0.1", port=3306, user="root", passwd="", db="test")
cursor = connection.cursor()
cursor.execute("CREATE TABLE justatest (name TEXT, ablob BLOB)")
try:
    names = 'aramis', 'athos', 'porthos'
    data = {}
    for name in names:
        datum = list(name)
        datum.sort()
        data[name] = cPickle.dumps(datum, 2)
    sql = "INSERT INTO justatest VALUES (%s, %s)"
    for name in names:
        cursor.execute(sql, (name, MySQLdb.escape_string(data[name])))
    # 恢复数据以进行检查
    sql = "SELECT name, ablob FROM justatest ORDER BY name;"
    cursor.execute(sql)
    for name, blob in cursor.fetchall():
        print name, cPickle.loads(blob), cPickle.loads(data[name])
finally:
    cursor.execute("DROP TABLE justatest;")
    connection.close()

'''
7.11 在PostgreSQL中储存BLOB
'''
'''
7.12 在SQLite中储存BLOB
'''
'''
7.13 生成一个字典将字段名映射为列号
'''
# 你想访问一个从DB API游标对象获得的数据，但你希望能够根据字段名访问列，而不是根据列号
def fields(cursor):
	""" 假设 DB API 2.0 游标对象已经被执行并返回了 """
	results = {}
	for column, desc in enumerate(cursor.description):
		results[desc[0]] = column
	return results

'''
7.14 利用dtuple实现对查询结果的灵活访问
'''
'''
7.15 打印数据库游标的内容
'''
# 你想使用合适的列头（以及可选的宽度）；来展示一次查询的结果，但你不新网在程序中采取硬编码的方式
def pp(cursor, data=None, check_row_lengths=False):
	if not data:
		data = cursor.fetchall()
	names = []
	lengths = []
	rules = []
	for col, field_description in enumerate(cursor.description):
		field_name = field_description[0]
		names.append(field_name)
		field_length = field_description[2] or 12
		field_length = max(field_length, len(field_name))
		if check_row_lengths:
			# 如果不可靠，复查字段长度
			data_length = max([len(str(row[col])) for row in data])
			field_length = max(field_length, data_length)
		lengths.append(field_length)
		rules.append('-' * field_length)
	format = " ".join(["%%-%ss" % l for l in lengths])
	result = [ format % tuple(names), format % tuple(rules) ]
	for row in data:
		result.append(format % tuple(row))
	return "\n".join(result)

'''
7.16 适用于各种DB API模块的单参数传递风格
'''
'''
7.17 通过ADO使用Microsoft Jet
'''
'''
7.18 从Jython Servlet访问JDBC数据库
'''
'''
7.19 通过Jython和ODBC获得Excel数据
'''
