#!/usr/bin/python3 

from server import *
from time import sleep

s = Server()
p = int(input("Enter port : "))
print ("port %d is available " % (p))
s.setPort(p)
s.setSharedDirectory("/home/himanshu")
s.setBandwidth(20)
s.startServer()

i = 0
while i < 5:
    sleep(0.5)
    print ("t=", i*0.5, "server is alive", s.server_proc.is_alive())
    i += 1

print ("port", p, "is available", isPortAvailable(p))
print ("stopping server")
s.stopServer()
print ("server is alive", s.server_proc.is_alive())
print ("port", p, "is available", isPortAvailable(p))


