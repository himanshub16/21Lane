from downloader import DownloadItem
from downman import DownloadManager

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

m = DownloadManager()
for di in dilist:
    m.addItem(di)
    # print (m.downloadQueue.__len__())
    # print(m.batchProcessor)


a=input()
m.stopDownloader()
