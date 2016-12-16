from ftplib import FTP
from time import sleep

class DownloadItem:
    def __init__(self, filename, host, port, sourcePath, destPath, size, signal):
        self.filename = filename 
        self.host = host 
        self.port = port 
        self.source = sourcePath 
        self.destination = destPath
        self.filesize = size
        self.completed = 0
        # self.guisignal = signal 
        self.completed = False
        self.worker = None 


class Downloader:
    def __init__(self, sema):
        self.di = None
        self.ftp = None 
        self.fileptr = None 
        self.running = False 
        self.sharedSem = sema
    
    def update(self, di):
        self.di = di 
    
    def abort(self):
        self.running = False 

    def cleanup(self):
        try:
            self.ftp.quit()
            self.fileptr.close() 
            self.running = False 
            del self.fileptr
            del self.ftp 
        except Exception as e:
            print ("cleanup", self.di.filename, e) 
        finally:
            self.di = None 
            self.ftp = None 
            self.fileptr = None 

    def callback(self, data):
        if not self.running:
            self.ftp.quit()
            self.running = False 
            # self.di.guisignal.raiseError()
            return
        self.fileptr.write(data)
        self.di.completed += len(data) 
        # self.di.guisignal.updateValues(self.completed)
            
    def download(self):
        try:
            self.fileptr = open(self.di.destination, "wb")
            self.ftp = FTP()
            self.ftp.connect(self.di.host, self.di.port)
            self.ftp.login()
            self.running = True 
            self.ftp.retrbinary("RETR "+self.di.source, self.callback)
        except Exception as e:
            print ("download:", self.di.filename, e)
            self.di.guisignal.raiseError()
        finally:
            print (self.di.filename, "completed by", self)
            self.di.worker = None 
            self.cleanup()
            self.sharedSem.release()
