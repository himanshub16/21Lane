#!/usr/bin/python3

# Using examples from https://pythonhosted.org/pyftpdlib/tutorial.html

from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import os 
import socket
from multiprocessing import Process 
from os.path import exists as path_exists
from customErrors import PortUnavailableError


def isPortAvailable(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',port))
    return not (result == 0)



class CustomHandler(FTPHandler):
    def on_connect(self):
        print ("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass


class Server:
    def __init__(self):
        self.port = 2121
        self.sharedDir = ""
        self.is_running = False 
        self.dtp_handler = ThrottledDTPHandler
        self.ftp_handler = CustomHandler
        self.ftp_handler.banner = "21Lane ready"

    def setPort(self, port):
        if isPortAvailable(port):
            self.port = port    
        else:
            raise PortUnavailableError

    def setSharedDirectory(self, path):
        if not path_exists(path):
            raise FileNotFoundError
        self.authorizer = DummyAuthorizer()
        self.authorizer.add_anonymous(path)
        self.ftp_handler.authorizer = self.authorizer

    def setBandwidth(self, netSpeed):
        self.dtp_handler.read_limit = netSpeed
        self.ftp_handler.dtp_handler = self.dtp_handler

    def startServer(self):
        self.server = FTPServer(('', self.port), self.ftp_handler)
        self.server_proc = Process(target=self.server.serve_forever)
        self.server_proc.start()
        self.is_running = True 

    def stopServer(self):
        if self.is_running:
            self.server.close_all()
            self.server_proc.terminate()
            self.server_proc.join()
            del self.server_proc
            self.server_proc = None 
            self.is_running = False 

