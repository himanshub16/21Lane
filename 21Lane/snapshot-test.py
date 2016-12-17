from snapshot import SnapshotUpdater
from time import sleep 

s = SnapshotUpdater("himanshu", 2121, "http://localhost:8000/cgi-bin/check.py")

i = 0
print ("t =", i, s.cache_proc)
s.updateDir("/home/himanshu/Downloads")
print ("t =", i, s.cache_proc)

sleep(10)
s.updateDir("/tmp")
    
s.abort()