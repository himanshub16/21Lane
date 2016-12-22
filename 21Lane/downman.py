from downloader import Downloader, DownloadItem
from os import cpu_count
from os import path 
from threading import Thread, BoundedSemaphore, Lock, Condition

max_workers = cpu_count()

class DownloadManager:
    def __init__(self):
        self.workerPool = []
        # semaphore blocks on 0
        self.workerSem = BoundedSemaphore(max_workers-1) 
        self.downloadQueue = []
        # to wakeup and suspend downloader subprocess
        self.queueCv = Condition()
        # classical producer consumer problem (applying condition variables)
        self.batchProcessor = None   
        self.running = False   
        for i in range(max_workers):
            self.workerPool.append(Downloader(self.workerSem))
        self.startDownloader()
        
    def startDownloader(self):
        if (not self.batchProcessor) or (not self.batchProcessor.is_alive()):
            self.batchProcessor = Thread(target=self.downloadManager)
            self.running = True 
            self.batchProcessor.start()
            print("download manager started")
        else:
            print('download manager already running', end=' ')

    def stopDownloader(self):
        try:
            self.running = False 
            self.queueCv.acquire()
            self.queueCv.notify() 
            self.queueCv.release()
        except ValueError:
            pass 
        self.batchProcessor.join()
        del self.batchProcessor
        self.batchProcessor = None 

    def addItem(self, di):
        self.queueCv.acquire()
        self.downloadQueue.append(di)
        print ('added', di.filename)
        self.queueCv.notify()
        self.queueCv.release()
        print ('notified')

    def removeItem(self, di):
        if di.worker:
            di.worker.abort()
        self.queueCv.acquire()
        self.downloadQueue.remove(di)
        self.queueCv.release()       
    
    def downloadManager(self):
        threadlist = []
        workingList = []
        while self.running:
            self.queueCv.acquire()
            while not self.downloadQueue and self.running:
                self.queueCv.wait()
            if not self.running:
                break
            di = self.downloadQueue.pop()
            workingList.append(di)
            self.queueCv.release()
            self.workerSem.acquire()
            print (self.workerSem._value)
            avail_workers = [ worker for worker in self.workerPool if not worker.running ]
            if not avail_workers:
                print ("WTF in worker synchronisation")
                raise Exception
            worker = avail_workers[0]
            di.worker = worker
            worker.update(di)
            th = Thread(target=worker.download)
            th.start()
            while not worker.running:
                pass 
            threadlist.append(th)
        
        print ('waiting for downloaders to exit')
        for thread in threadlist:
            thread.join()
        print ("download manager quits")

