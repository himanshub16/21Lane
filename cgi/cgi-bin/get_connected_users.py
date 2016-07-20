#!/usr/bin/python3
from tinydb import TinyDB, Query, where
import cgi, cgitb
import os, sys
import json

cgitb.enable()
ls = os.listdir
pwd = os.getcwd()
dbname = os.path.join(pwd, 'data'+os.sep+'connected_users.json')

if not os.path.isfile(dbname):
	sys.exit()

db = TinyDB(dbname)
# raw_data = db.all()
# data = json.loads(raw_data)	

print("Content-type:application/json")

print()

jsonData = dict()
for row in db.all():
	sessid = row['SESSION_ID']
	row.pop('SESSION_ID')
	row.pop('FILENAME')
	jsonData[sessid] = row

print (json.dumps(jsonData))