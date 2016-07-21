#!/usr/bin/python3
import cgi, cgitb, os
from tinydb import TinyDB
cgitb.enable()
print("Content-type:text/html")
print()	

ls = os.listdir
pwd = os.getcwd()

datadir = os.path.join(pwd, 'data')
dbname = os.path.join(datadir, 'connected_users.json')

print(datadir, 'is the data directory <br />')
print(dbname, 'is the dbname <br/>')

form = cgi.FieldStorage()
sharesize = form.getvalue('sharesize')
action = form.getvalue('action')

print(form, 'is the form <br/>')
print(sharesize, 'is the sharesize <br/>')
print(action, 'is the asked action <br/>')

db = TinyDB(dbname)
print(db.all(), '<br/>')
print("hey jude, don't make it bad")
print("<br />")
print(os.environ['HOME'], 'is the home directory')
print("<br />")
print(os.path.expanduser('~'), 'is the current user')
print("<br />")
print(os.getcwd(), 'is the current working directory')
print("<br />")

filename = os.path.join(os.path.join(os.getcwd(), 'cgi-bin'), 'actions.py')
f = open(filename, 'r') 
print(f.read())
# print(os.path.abspath('.'))