from PyQt5.QtCore import pyqtSignal, QObject

class DownloadItemUpdater(QObject):
    signal = pyqtSignal()

    def updateValues():
        self.signal.emit()
    
    def raiseError():
        self.signal.emit()
