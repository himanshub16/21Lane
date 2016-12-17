#!/usr/bin/python3

import cgi, cgitb
import socket 
import os
import json 
from time import time 
from hashlib import md5
from sys import exit

cgitb.enable() # for debugging 

SHARE_CAP = 10737418240 # 10 GB
USER_DB = "21lane_db.json"

def checkConnection(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, int(port)))
    return (result == 0)

def getSessionId(ip):
    mystr = str(time()) + ip
    return md5(mystr.encode()).hexdigest()

def sanitize(s):
    try:
        return s.replace('\"', '')
    except AttributeError:
        return None

def getUsers():
    dic = {}
    try:
        f = open(USER_DB)
        dic = json.loads(f.read())
        f.close()
    except FileNotFoundError:
        pass
    return dic 

def checkUser(db, sessid):
    return (sessid in db.keys())

def updateDb(db):
    with open(USER_DB, "w") as f:
        f.write(json.dumps(db))

def login(sessid, ip, port, sharedSize):
    reachable = checkConnection(ip, port) 
    present = checkUser(db, sessid)
    db = getUsers()
    if present:
        if reachable:
            db[sessid] = {
                "ip": ip, 
                "port": port, 
                "sharedSize": sharedSize
            }
            updateDb(db)
        else:
            logout(sessid)
    elif reachable:
        sessid = getSessionId(ip)
        db[sessid] = {
            "ip": ip, 
            "port": port, 
            "sharedSize": sharedSize
        }
        updateDb(db)
    return sessid 

def logout(sessid):
    db = getUsers()
    if checkUser(sessid):
        db.pop(sessid)
    updateDb(db)

def validateRequest(publicName, port, sharedSize, sessionId, action):
    if action is "login":
        if ((port is None) or \
            (publicName is None) or \
            (sharedSize is None) ):
            return False 
    elif action is "logout":
        if (sessionId is None):
            return False 
    return True 


remoteIP = os.environ.get("REMOTE_ADDR")
form = cgi.FieldStorage()
port = form.getvalue("port")
sharedSize = form.getvalue("sharedSize")
publicName = form.getvalue("publicName")
sessionId = form.getvalue("sessionId")
action = form.getvalue("action")

print("Content-type: text/plain")
print()
if not action:
    print("failed")
    exit(1)

action = sanitize(action)
sessionId = sanitize(sessionId)
port = sanitize(port)
remoteIP = sanitize(remoteIP)
publicName = sanitize(publicName)

if validateRequest(publicName, port, sharedSize, sessionId, action):
    if "login" in action:
        retval = login(sessionId, remoteIP, port, sharedSize)
        print (retval) 
    elif "logout" in action:
        logout(sessid) 
        print ("success")
    else:
        print("failed")
else:
    print("failed")

