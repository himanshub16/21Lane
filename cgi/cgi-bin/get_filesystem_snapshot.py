#!/usr/bin/python3
# credits : http://stackoverflow.com/a/25226267 (Emanuele Paolini)

import os, json
import sys, cgi, cgitb
from pprint import pprint
import threading, time

# print('Content-type:application/json\r\n')
print('Content-type:application/json\r\n')
total_size = 0

# def path_to_dict(path):
# 	d = {'name': os.path.basename(path)}
# 	try:
# 		if os.path.isdir(path):
# 			d['type'] = 'directory'
# 			d['children'] = [ path_to_dict(os.path.join(path, x)) for x in os.listdir(path) ]
# 		else:
# 			d['type'] = 'file'
# 			d['size'] = os.path.getsize(path)
# 			global total_size
# 			total_size += os.path.getsize(path)
# 	except Exception as e:
# 		pass
# 	return d
dic = {}
totalsize = 0
ip = '192.168.1.5:2121'
def path_to_dict(path, l):
	global dic, totalsize
	try:
		if os.path.isdir(path):
			for x in os.listdir(path):
				path_to_dict(os.path.join(path, x), l)
		else:
			dic[os.path.basename(path)] = { "size" : os.path.getsize(path), "fullpath" : ip+path[l:] }
			totalsize += os.path.getsize(path)
	except Exception as e:
		pass

# data = path_to_dict(dic, '.', len(os.getcwd()))
# dic['total_size'] = total_size
# data = json.dumps(dic, indent=2)
p = len(os.path.abspath('.'))
def display():
	path_to_dict(os.getcwd(), p)
	dic['totalsize'] = totalsize
	print(json.dumps(dic, indent=2))

n = 0
t = threading.Timer(5.0, display, [])
while(n < 3):
	t.start()
	time.sleep(3)
	n += 1