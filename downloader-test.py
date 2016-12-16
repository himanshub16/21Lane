from downloader import DownloadItem, Downloader
from threading import BoundedSemaphore, Thread

filelist = [ {
        "filename": "file1",
        "host": "localhost",
        "port": 2121,
        "source": "/Downloads/file1",
        "destination": "/tmp/file1"
    }, {
        "filename": "file2",
        "host": "localhost",
        "port": 2121,
        "source": "/Downloads/file2",
        "destination": "/tmp/file2"
    }, {
        "filename": "file3",
        "host": "localhost",
        "port": 2121,
        "source": "/Downloads/file3",
        "destination": "/tmp/file3"
    }, {
        "filename": "file4",
        "host": "localhost",
        "port": 2121,
        "source": "/Downloads/file4",
        "destination": "/tmp/file4"
    }, {
        "filename": "file5",
        "host": "localhost",
        "port": 2121,
        "source": "/Downloads/file5",
        "destination": "/tmp/file5"
    }
]

dilist = []
for item in filelist:
    di = DownloadItem(item["filename"], item["host"], item["port"], item["source"], item["destination"], 780, None)
    dilist.append(di)


workerlist = []
sem = BoundedSemaphore(3)
for i in range(3):
	workerlist.append(Downloader(sem))


i = 2
print(workerlist)
print()
pool = []
while dilist:
	di = dilist.pop()
	avail = [ worker for worker in workerlist if not worker.running ]
	print(len(avail), 'workers available')
	while len(avail) == 0:
		avail = [ worker for worker in workerlist if not worker.running ]

	worker = avail[0]
	print (di.filename, 'with',workerlist.index(worker))
	worker.update(di)
	sem.acquire()
	th = Thread(target=worker.download)
	th.start()
	while (not worker.running):
		pass
	pool.append(th)

for thread in pool:
	thread.join()
