#!/usr/bin/python3

# code for file browser 
from ftplib import FTP
from copy import deepcopy
from os.path import join

class Browser:
    def __init__(self, parent):
        self.qt_parent = parent 
        # the parent of all widgets created for browser 

    def getFileList(self, host, port, pwd):
        self.filelist = None 
        ftp = FTP()
        # the following is a result of hours of manual tuning and string manipulation
        # please bear with the complexity
        try:
            l = []
            ftp.connect(host, port)
            ftp.login()
            ftp.dir(pwd, l.append)
            ftp.quit()
            m = deepcopy(l)
            for i in range(len(l)):
                l[i] = l[i].split()
            tmplist = {}
            for i in range(len(l)):
                # l[i] = [ x for x in l[i] if x!= '' ] # no need if using string.split(), which was string.split(' ') earlier
                isDir = l[i][0].startswith('d')
                filesize = int(l[i][4])
                for item in l[i][:8]:
                    m[i] = m[i].replace(item, '', 1)
                filename = m[i].strip()
                tmplist[i] = {'isDir':isDir, 'filesize':filesize, 'filename':filename, 'pathname':join(pwd, filename) }
        except Exception as e:
            ftp.close()
            print('error occured')
        else:
            self.filelist = list(tmplist.values())
        return self.filelist

    def getRecursiveList(self, host, port, pwd, depth=1):
        try:
            fl = self.getFileList(host, port, pwd)
            for file in fl:
                if file["isDir"]:
                    self.getRecursiveList(host, port, deepcopy(file["pathname"]), depth+1)
                else:
                    self.recfilelist.append(file)
        except RecursionError:
            return 
        except Exception as e:
            print("Error occured", e)
            raise e

    def getRecursiveFileList(self, host, port, pwd):
        self.recfilelist = []
        self.getRecursiveList(host, port, deepcopy(pwd))
        meta = { "totalFiles": 0, "totalSize": 0 }
        for file in self.recfilelist:
            meta["totalFiles"] += 1
            meta["totalSize"] += file["filesize"]
        return meta 