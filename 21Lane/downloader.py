from ftplib import FTP

class raiseError(Exception):
    pass 

class Downloader:
    def __init__(self):
        self.filename = None
        self.host = ""
        self.port = 2121
        self.source = ""
        self.destination = ""
        self.filesize = 0
        self.completed = 0
        self.ftp = FTP()
        self.guisignal = None
        self.fileobj = None

    def callback(self, data):
        file.write(data)
        self.completed += len(data)
        self.guisignal.updateValues(self.completed)

    def cleanup(self):
        try:
            self.ftp.quit()
            self.fileobj.close()
        except Exception as e:
            pass 
        finally:
            self.__init__()

    def download(self, host, port, filename, source, destination, size, signal):
        try:
            self.fileobj = open(destination, 'w')
            self.guisignal = signal 
            self.filesize = size
            self.filename = filename 
            self.ftp.connect(host, port)
            self.ftp.login()
            self.ftp.retrbinary("RETR "+destination, callback)
        except Exception as e:
            self.guisignal.raiseError()
        finally:
            self.cleanup()
