#!/usr/bin/python

import ftplib
import sys
import json
from copy import deepcopy

dirList = []

host = sys.argv[1]
port = int(sys.argv[2])
pwd  = sys.argv[3]


try:
	l = []
	cl = ftplib.FTP()
	cl.connect(host = host, port = port)
	cl.login()
	cl.dir(pwd, l.append)
	cl.quit()
	m = deepcopy(l)
	for i in range(len(l)):
		l[i] = l[i].split()

	for i in range(len(l)):
		isDir = l[i][0].startswith('d')
		fileSize = int(l[i][4])
		for item in l[i][:8]:
			m[i] = m[i].replace(item, '', 1)

		fileName = m[i].strip()
		dirList.append( {
			"isDir": isDir,
			"fileSize": fileSize,
			"fileName": fileName,
			"ftpPath": pwd+'/'+fileName,
			"URL": "ftp://"+host+":"+str(port)+'/'+pwd+"/"+fileName
			})
except Exception as e:
	cl.close()
	print "Error occured", e
finally:
	with open("dirlist.json", 'w') as f:
		f.write(json.dumps(dirList))

