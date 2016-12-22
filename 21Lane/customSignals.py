from PyQt5.QtCore import pyqtSignal, QObject

class DownloadItemUpdater(QObject):
    signal = pyqtSignal()

    def updateValues(self):
        self.signal.emit()
    
    def raiseErrors(self):
        self.signal.emit()


class ServerStatsUpdater(QObject):
    clientConnect = pyqtSignal()
    clientDisconnect = pyqtSignal()
    fileTransfer = pyqtSignal(int)

    def connected(self):
        self.clientConnect.emit()

    def disconnected(self):
        self.clientDisconnect.emit()

    def transferred(self, filesize):
        self.fileTransfer.emit(filesize)


class DownloadItemUpdater(QObject):
    progress = pyqtSignal(int)
    complete = pyqtSignal()
    error = pyqtSignal()

    def updateProgress(self, value):
        self.progress.emit(value)
    
    def completed(self):
        self.complete.emit()

    def raiseError(self):
        self.error.emit()
