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
