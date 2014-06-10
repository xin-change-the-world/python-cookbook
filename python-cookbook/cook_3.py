#/usr/bin/env pyton
# -*- coding: utf-8 -*-
'''
#
#
# python cookbook 第三章 时间和财务计算
# Auther：张广欣
# Date：2014-06-10
#
#
'''
###############################
'''
3.1 计算昨天和明天的日期
'''
import datetime
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)
print yesterday, today, tomorrow
#增加一年
anniversary = today + datetime.timedelta(days=365)
#获得现在的时间
t = datetime.datetime.today()
#增加一秒
t2 = t + datetime.timedelta(seconds=1)
#增加一小时
t3 = t + datetime.timedelta(seconds=3600)

'''
3.2 寻找上一个星期五
'''
import datetime, calendar
lastFriday = datetime.date.today()
oneday = datetime.timedelta(days=1)
while lastFriday.weekday() != calendar.FRIDAY:
	lastFriday -= oneday
print lastFriday.strftime('%Y-%m-%d')
#另一种方法，resolution可能会让你犯错
import datetime, calendar
lastFriday = datetime.date.today()
while lastFriday.weekday() != calendar.FRIDAY:
	lastFriday -= datetime.date.resolution
print lastFriday.strftime('%Y-%m-%d')

'''
3.3 计算日期之间的时段
'''
from dateutil import rrule
import datetime
def weeks_between(start_date, end_date):
	weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
	return weeks.count()
starts = [datetime.date(2005,01,04), datetime.date(2005,01,03)]
end = datetime.date(2005,01,10)
for s in starts:
	days = rrule.rrule(rrule.DAILY, dtstart=s, until=end).count()
	print "%d days shows as %d weeks " % (days, weeks_between(s,end))

'''
3.4 计算歌曲的总播放时间
'''
import datetime
def totaltimer(times):
	td = datetime.timedelta(0)
	duration = sum([
		datetime.timedelta(minutes=m, seconds=s) for m, s in times
		], td)
	return duration
times1 = [(2, 36),(3, 35),(3, 45),]
times2 = [(3, 0),(5, 13),(4, 12),(1, 10),]
assert totaltimer(times1) == datetime.timedelta(0, 596)
assert totaltimer(times2) == datetime.timedelta(0, 815)
print ("Tests passed.\n"
		"First test total: %s\n"
		"Second test total: %s" % (
			totaltimer(times1), totaltimer(times2)))

'''
3.5 计算日期之间的工作日
'''
from dateutil import rrule
import datetime
def workdays(start, end, holidays=0, days_off=None):
	if days_off is None:
		days_off = 5, 6 #默认：周六和周日
	workdays = [x for x in range(7) if x not in days_off]
	days = rrule.rrule(rrule.DAILY, dtstart=start, until=end, byweekday=workdays)
	return days.count() - holidays
testdates=[(datetime.date(2004,9,1), datetime.date(2004,11,14), 2),
		  (datetime.date(2003,2,28), datetime.date(2003,3,3), 1),]
def test(testdates, days_off=None):
	for s, e, h in testdates:
		print 'total workdays from %s to %s is %s with %s holidays' % (s, e, workdays(s, e, h, days_off), h)

test(testdates)
test(testdates, days_off=[6])

'''
3.6 自动查询节日
'''
'''
3.7 日期的模糊查询
'''
#你的程序需要读取并接受一些并不符合标准的“yyyy,mm,dd”datetime格式
import datetime
import dateutil.parser

def tryparse(date):
    # dateutil.parse需要一个字符串参数：根据一些惯例，我们可以从4种date参数创建一个
    kwargs = { }
    if isinstance(date, (tuple, list)):
        date = ''.join([str(x) for x in date])
    elif isinstance(date, int):
        date = str(date) 
    elif isinstance(date, dict):
        kwargs = date
        date = kwargs.pop('date')
    try:
        try:
            parsedate = dateutil.parser.parse(date, **kwargs)
            print 'Sharp %r -> %s' % (date, parsedate)
        except ValueError:
            parsedate=dateutil.parser.parse(date, fuzzy=True, **kwargs)
            print 'Fuzzy %r -> %s' % (date, parsedate)
    except Exception, err:
        print 'Try as I may, I cannot parse %r (%s)' % (date, err)
tests = ("January 3, 2003",
        (5, "Oct", 55),
        "Thursday, November 18",
        "7/24/04",
        "24-7-2007",
        {'date':"5-10-1955","dayfirst":True},
        "5-10-1955",
        19950317
        )
for test in tests:
    tryparse(test)

'''
3.8 检查夏令时是否正在实行
'''
import time
def is_dst():
    return bool(time.localtime().tm_isdst)
print is_dst()

'''
3.9 时区转换
'''
#第三方包dateutil中对datetime提供了时区支持
'''
from dateutil import tz
import datetime
posixstr = "CET-1CEST-2,M3.5.0/02:00,M10.5.0/03:00"
spaintz = tz.tzstr(posixstr)
print datetime.datetime.now(spaintz).ctime()
'''

'''
3.10 反复执行某个命令
'''
'''
import time, os, sys
def main(cmd, inc=60):
	while True:
		os.system(cmd)
		time.sleep(inc)
'''

'''
3.11 定时执行命令
'''
#这正是标准库sched模块所针对的任务
import time, os, sys, sched
schedule = sched.scheduler(time.time, time.sleep)
def perform_command(cmd, inc):
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)
def main(cmd, inc=60):
    schedule.enter(0, 0, perform_command, (cmd, inc))
    schedule.run()

'''
3.12 十进制数学计算
'''
import decimal
d1 = decimal.Decimal('0.3') #指定一个十进制对象
print d1/3
print (d1/3)*3
f1 = 0.3
print f1/3
print (f1/3)*3

'''
3.13 将十进制数用于货币处理
'''

'''
3.14 用Python实现的简单加法器
'''
#你想用Python制作一个简单的加法器，使用精确的十进制数（而不是二进制浮点数）
#并以整洁的纵列显示计算结果
#为了执行计算，必须使用decimal模块
import decimal, re, operator
parse_input = re.compile(r'''(?x)        #允许RE中的注释和空白符
                        (\d+\.?\d*)      #带有可选的小数部分的数
                        \s*              #可选的空白符
                        ([-+/*])         #运算符
                        $                #字符串结束
                        ''')

oper = { '+': operator.add, '-':operator.sub, '*':operator.mul, '/':operator.truediv}
total = decimal.Decimal('0')
def print_total():
    print '== == =\n', total
print """Welcome to Adding Machine:
Enter a number and operator,
an empty line to see the current subtotal,
or q to quit:
"""
while True:
    try:
        tape_line = raw_input().strip()
    except EOFError:
        tape_line = 'q'
    if not tape_line:
        print_total()
        continue
    elif tape_line == 'q':
        print_total()
        break
    try:
        num_text, op = parse_input.match(tape_line).groups()
    except AttributeError:
        print 'Invalid entry:%r' % tape_line
        print 'Enter number and operator, empty line for total, q to quit'
        continue
    total = oper[op](total, decimal.Decimal(num_text))

'''
3.15 检查信用卡校验和
'''
#需要检查一个信用卡号是否遵循工业标准Luhn校验和算法
def cardLuhnCheckSumIsValid(card_number):
    """通过luhn mod-10 校验和算法检查信用卡号"""
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range(num_digits):
        digit = int(card_number[count])
        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit
    return (sum % 10) == 0

'''
3.16 查看汇率
'''
