from snapshot import SnapshotUpdater
from time import sleep 

s = SnapshotUpdater()
s.updateInfo("himanshu", "http://localhost:8000/cgi-bin/check.py", 2121)

i = 0
print ("t =", i, s.cache_proc)
s.updateDir("/home/himanshu/Downloads")
print ("t =", i, s.cache_proc)
while not s.is_running:
    pass 
sleep(2)   
print (s.sessionId)
sleep(10)
s.updateDir("/tmp")
print (s.sessionId)    
s.abort()