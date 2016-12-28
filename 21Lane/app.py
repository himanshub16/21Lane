#!/usr/bin/python3 

from server import Server
from downman import DownloadManager
from exchangeClient import ExchangeClient 
from browser import Browser
from downloader import DownloadItem
from config import Settings
from customSignals import *
from customErrors import * 

from webbrowser import open as xdg_open
from mimetypes import guess_type as guess_mime
from os.path import join as join_path
from os.path import dirname as get_dirname

import resources_rc
from form import Ui_mainWindow 
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.QtWidgets import QHBoxLayout, QProgressBar, QLabel, QPushButton, QFrame
from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon, qApp
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt 

from PyQt5.QtNetwork import QNetworkInterface, QAbstractSocket, QHostAddress


KB = 1024
MB = 1048576
GB = 1073741824

def toHumanReadable(bytes):
    inKB = round(bytes / KB, 2)
    inMB = round(bytes / MB, 2) 
    inGB = round(bytes / GB, 2) 
    if inGB:
        return str(inGB)+" GB"
    elif inMB:
        return str(inMB)+" MB"
    elif inKB:
        return str(inKB)+" KB"
    else:
        return str(bytes)+ " bytes"


def getAllAddresses():
    addresses = QNetworkInterface.allAddresses()
    required = []
    for address in addresses:
        if (address.protocol() == QAbstractSocket.IPv4Protocol) and \
            (address != QHostAddress(QHostAddress.LocalHost)):
            required.append(address.toString())
    return required


class GUI(Ui_mainWindow):
    def __init__(self, window):
        super().__init__()
        self.setupUi(window)
        self.window = window 
        self.settings = Settings() 
        self.window.closeEvent = self.closeEvent
        self.server = Server()
        self.downman = DownloadManager()
        self.browser = Browser()
        # snapshot updater is to be started on exchange connect
        self.xchgClient = ExchangeClient()  
        self.lastKnownDir = "/tmp"
        self.destPrefix = ''
        self.userlist = None 
        self.di_list = []
        self.addEventListeners() 
        self.loadSettings()
        self.browserTable.setColumnHidden(0, True)
        self.userListTable.setColumnHidden(0, True)
        self.tabWidget.setCurrentIndex(0)
        self.urlFrame.setVisible(False)
        self.downloadsScrollArea.setStyleSheet(" \
            download_item { \
                border: 1px solid grey; \
            } \
        ")
        self.window.setWindowIcon(QIcon(":/images/favicon.ico"))
        self.window.setWindowTitle("21Lane")
        self.setupSystemTray()
        self.window.show()


    def loadSettings(self):
        self.settings.load()
        self.publicNameInput.setText(self.settings.configDic["publicName"])
        self.port.setValue(self.settings.configDic["port"])
        self.sharedLocationInput.setText(self.settings.configDic["sharedDir"])
        self.downloadLocationInput.setText(self.settings.configDic["downloadDir"])
        self.speedLimitSlider.setValue(self.settings.configDic["speedLimit"])
        self.speedLimitSpin.setValue(self.settings.configDic["speedLimit"])
        self.exchangeURLInput.setText(self.settings.configDic["exchangeURL"])


    def keyPressedEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()


    def closeEvent(self, event):
        if not type(event) == bool:
            self.showDialog(False)
            self.activateAction.setChecked(False)
            event.ignore()
            return
        if self.server.isRunning():
            self.server.stopServer()
        if self.xchgClient.isRunning():
            print ('attempting to shut down exchange client')
            self.xchgClient.quit()
            print ('asked to end xchgclient politely')
            if not self.xchgClient.wait(1):
                print('forced closure of xchgclient required')
                self.xchgClient.terminate()
            print('xchgclient forcefully closed')
        if self.downman.running:
            self.downman.stopDownloader()
        qApp.exit()


    def showMessage(self, maintext=None, subtext=None):
        QMessageBox.information(self.window, maintext, subtext, QMessageBox.Ok, QMessageBox.Ok)


    def getPathFromDialog(self):
        return QFileDialog.getExistingDirectory(self.window, "Select folder", self.lastKnownDir, QFileDialog.ShowDirsOnly)


    def addEventListeners(self):
        self.speedLimitSlider.valueChanged[int].connect(self.updateSpeedLimit)
        self.speedLimitSpin.valueChanged[int].connect(self.updateSpeedLimit)
        self.sharedLocationBtn.clicked.connect(self.showDirectorySelector)
        self.downloadLocationBtn.clicked.connect(self.showDirectorySelector)
        self.toggleShareBtn.setText("Start Sharing")
        self.toggleShareBtn.clicked.connect(self.toggleShare)
        self.server.ftp_handler.stats.clientConnect.connect(self.statClientConnected)
        self.server.ftp_handler.stats.clientDisconnect.connect(self.statClientDisconnected)
        self.server.ftp_handler.stats.fileTransfer[int] .connect(self.statFileTransferred)
        self.reloadUsersBtn.clicked.connect(self.loadUsers)
        self.browserInput.returnPressed.connect(self.browserGoBtn.click)
        self.browserGoBtn.clicked.connect(self.loadBrowserTable)
        self.browserHomeBtn.clicked.connect(self.loadBrowserTable)
        self.browserPrevBtn.clicked.connect(self.handleBackBtnClick)
        self.userListTable.doubleClicked.connect(self.showBrowser)
        self.browserTable.doubleClicked.connect(self.handleFileSelection)
        self.developerLink.linkActivated.connect(xdg_open)
        self.projectLink.linkActivated.connect(xdg_open)
        self.stats_connected.setText("hello ")

    def showDirectorySelector(self, event):
        if self.window.sender() is self.downloadLocationBtn:
            self.downloadLocationInput.setText(self.getPathFromDialog())
            self.destPrefix = self.downloadLocationInput.text() 
        elif self.window.sender() is self.sharedLocationBtn:
            self.sharedLocationInput.setText(self.getPathFromDialog()) 


    def updateSpeedLimit(self, value):
        self.speedLimitSlider.setValue(value)
        self.speedLimitSpin.setValue(value)


    def statClientConnected(self):
        print("man connected")
        self.server.connected += 1
        self.stats_connected.setText(str(self.server.connected))
        print(self.server.connected, self.stats_connected.text())
    

    def statClientDisconnected(self):
        print ('amn disconnected')
        self.server.connected -= 1
        self.stats_connected.setText(str(self.server.connected))
        print(self.server.connected)


    def statFileTransferred(self, filesize):
        self.server.bytesTransferred += filesize 
        self.server.filesTransferred += 1
        self.stats_files.setText(str(self.server.filesTransferred))
        self.stats_bytes.setText(toHumanReadable(self.server.bytesTransferred))


    def toggleShare(self):
        try:
            if  (not self.publicNameInput.text()) or \
                (not self.port.value()) or \
                (not self.sharedLocationInput.text()):
                raise FormIncompleteError 
            if self.xchgClient.isRunning():
                self.xchgClient.quit()
                if not self.xchgClient.wait(1):
                    self.xchgClient.terminate()
            if self.server.isRunning():
                self.server.stopServer()
                self.toggleShareBtn.setText("Start Sharing")
                self.toggleShareBtn.setIcon(QIcon(":/images/failed.svg"))
                self.urlFrame.setVisible(False)
            else:
                self.server.setPort(self.port.value())
                self.server.setSharedDirectory(self.sharedLocationInput.text())
                self.server.start()
                if not self.exchangeURLInput.text():
                    self.xchgClient.updateInfo(self.publicNameInput.text(), None, self.port.value())
                else:
                    self.xchgClient.updateInfo(self.publicNameInput.text(), self.exchangeURLInput.text(), self.port.value())                         
                self.xchgClient.updateDir(self.sharedLocationInput.text())
                self.settings.update(self.publicNameInput.text(), self.port.value(), \
                    self.sharedLocationInput.text(), self.downloadLocationInput.text(), self.speedLimitSlider.value(), self.exchangeURLInput.text())
                self.toggleShareBtn.setText("Stop Sharing")
                self.toggleShareBtn.setIcon(QIcon(":/images/complete.svg"))
                addresses = getAllAddresses()
                if len(addresses) != 0:
                    lblstr = "<html><body>"
                    current = 0
                    end = len(addresses)-1
                    for addr in addresses:
                        hyperlink = 'ftp://'+addr+':'+str(self.server.port)
                        lblstr += "<a href=\'"+hyperlink+"\'>"+hyperlink+"</a>"
                        if current != (end-1):
                            lblstr += '\n'
                        current += 1
                    lblstr += "</body></html>"  
                    self.urlLabel.setText(lblstr)
                    self.urlFrame.setVisible(True)                
        except FileNotFoundError:
            self.showMessage("Don't fool me", "Shared location doesn't exist")
        except PortUnavailableError:
            self.showMessage("Port unavailable", "Please select some other port number")
        except FormIncompleteError:
            self.showMessage("Form incomplete", "Please fill in proper values!")


    def loadUsers(self):
        userlist = self.xchgClient.getUserList()  
        self.userlist = userlist      
        if not userlist:
            self.showMessage("Sorry", "Cannot retrieve list of users")
            return 
        table = self.userListTable
        table.clearContents()
        table.setRowCount(len(userlist))
        for i, entry in enumerate(userlist):
            table.setItem(i, 0, QTableWidgetItem(str(i)))
            table.setItem(i, 1, QTableWidgetItem(toHumanReadable(int(entry["sharedSize"]))))
            table.setItem(i, 2, QTableWidgetItem(entry["publicName"]))


    def showBrowser(self):
        if not self.userlist:
            return 
        current = self.userListTable.selectedItems()[0]
        index = int(self.userListTable.item(current.row(), 0).text())
        user = self.userlist[index]
        self.browser.update(user["ip"], int(user["port"]))
        self.tabWidget.setCurrentIndex(2)
        self.browserInput.setText("/")
        self.browserGoBtn.click()


    def loadBrowserTable(self):
        pwd = self.browserInput.text()
        filelist = []
        try:
            if not self.browser.pathExists(self.browser.host, self.browser.port, pwd):
                self.showMessage("Error", "The path does not exist!")
                return 
            self.browser.historyStack.append(pwd)
            filelist = self.browser.getFileList(self.browser.host, self.browser.port, pwd)
            self.browser.filelist = filelist
        except ConnectionRefusedError:
            self.showMessage("Offline", "The remote machine cannot be contacted!\nBetter luck next time.")
            self.tabWidget.setCurrentIndex(1)
        table = self.browserTable
        table.clearContents()
        table.setRowCount(len(filelist))
        for i, file in enumerate(filelist):
            table.setItem(i, 0, QTableWidgetItem(str(i)))
            table.setItem(i, 1, QTableWidgetItem(QIcon(":images/download.png"), ""))
            table.setItem(i, 2, QTableWidgetItem(toHumanReadable(file["filesize"])))
            if file["isDir"]:
                table.setItem(i, 3, QTableWidgetItem(QIcon(":/images/folder.png"), ""))
            else:
                table.setItem(i, 3, QTableWidgetItem(guess_mime(file["filename"])[0]))
            table.setItem(i, 4, QTableWidgetItem(file["filename"]))


    def handleBackBtnClick(self):
        if not self.userlist:
            self.showMessage("Confused", "What should I load? \nFind someone from list of connected users.")
            return 
        if len(self.browser.historyStack) < 2:
            self.showMessage("Sorry", "Hey, there's no looking back!")
            return 
        self.browser.historyStack.pop()
        prev = self.browser.historyStack.pop()
        self.browserInput.setText(prev)
        self.loadBrowserTable()


    def handleFileSelection(self):
        if not self.browser.filelist:
            return 
        current = self.browserTable.selectedItems()[0]
        index = int(self.browserTable.item(current.row(), 0).text())
        file = self.browser.filelist[index]
        print ("index", index, file["pathname"], current.text())
        if file["isDir"] and current.column() is not 1:
            pwd = join_path(self.browserInput.text(), file["pathname"])
            self.browserInput.setText(pwd)
            self.browserGoBtn.click()
            return 
        # a download is to be handled
        print ("downloading directory", file["filename"])
        # decide it is a file or directory
        if not self.destPrefix:
            destDir = join_path(self.getPathFromDialog())
        else:
            destDir = self.destPrefix
        meta = None 
        if file["isDir"]:
            meta = self.browser.getRecursiveFileList(self.browser.host, self.browser.port, file["pathname"])
            filelist = self.browser.recfilelist 
        else:
            meta = { "totalFiles": 1, "totalSize":file["filesize"] }
            filelist = [ file ]
        signal = DownloadItemUpdater() 
        diui = self.createDownloadItemBox(file["filename"], meta["totalSize"])
        dilist = []
        for item in filelist:
            di = DownloadItem(item["filename"], self.browser.host, self.browser.port, item["pathname"], join_path(destDir, item["filename"]), item["filesize"], signal)
            di.updateGuiComponents(diui)
            dilist.append(di)
        
        # create callbacks for gui events
        def cancelCallback():
            for di in dilist:
                di.cancel()
            diui["cancelBtn"].setIcon(QIcon(":/images/reload.png"))
            diui["cancelBtn"].clicked.disconnect()
            diui["cancelBtn"].clicked.connect(retryCallback)
        
        def updateProgressCallback(progress):
            sum = 0
            for di in dilist:
                sum += di.completed
            diui["progress"].setValue(sum)
            diui["completion"].setText(toHumanReadable(sum))

        def retryCallback():
            print ("retrying")
            di.completed = 0
            self.downman.addItem(di)
            diui["cancelBtn"].clicked.disconnect()
            diui["cancelBtn"].clicked.connect(cancelCallback)
            diui["cancelBtn"].setIcon(QIcon(":/images/cancel.png"))

        def errorCallback():
            diui["completion"].setText("Failed")
            cancelCallback()

        def completeCallback():
            diui["completion"].setText("Completed")
            diui["cancelBtn"].clicked.disconnect()
            diui["cancelBtn"].setToolTip("Open")
            diui["cancelBtn"].setIcon(QIcon(":/images/open.png"))
            diui["cancelBtn"].clicked.connect(openFile)

        def openFile():
            xdg_open(join_path(destDir, file["filename"]))

        def openDir():
            xdg_open(destDir)

        diui["cancelBtn"].clicked.connect(cancelCallback)
        signal.progress[int].connect(updateProgressCallback)
        signal.error.connect(errorCallback)
        signal.complete.connect(completeCallback)
        diui["openDestBtn"].clicked.connect(openDir)
        self.downloadsLayout.insertWidget(0, diui["widget"])
        for entry in dilist:
            self.downman.addItem(entry)
        # print ("downloading", di.filename, di.filesize, "to")


    def createDownloadItemBox(self, filename, filesize):
        diui = {}
        frame = QFrame(self.window)
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout()
        filesize = filesize if not filesize is 0 else 1
        diui["layout"] = layout
        diui["widget"] = frame
        diui["filename"] = QLabel(filename)
        diui["filename"].setToolTip(filename)
        diui["filename"].setMaximumWidth(30)
        diui["filesize"] = QLabel(toHumanReadable(filesize))
        diui["filesize"].setAlignment(Qt.AlignCenter)
        diui["progress"] = QProgressBar()
        diui["progress"].setRange(0, filesize)
        diui["completion"] = QLabel("Waiting...")
        diui["completion"].setAlignment(Qt.AlignCenter)
        diui["cancelBtn"] = QPushButton(QIcon(":/images/cancel.png"), '')
        diui["openDestBtn"] = QPushButton(QIcon(":/images/folder.png"), '')
        diui["cancelBtn"].setToolTip("Cancel download")
        diui["openDestBtn"].setToolTip("Open folder")
        diui["layout"].addWidget(diui["filename"])
        diui["layout"].addWidget(diui["filesize"])
        diui["layout"].addWidget(diui["progress"])
        diui["layout"].addWidget(diui["completion"])
        diui["layout"].addWidget(diui["openDestBtn"])
        diui["layout"].addWidget(diui["cancelBtn"])
        diui["layout"].setSpacing(0)
        layout.setContentsMargins(5,2,5,2)
        layout.setSpacing(6)
        layout.setStretch(0, 3)
        layout.setStretch(1, 2)
        layout.setStretch(2, 5)
        layout.setStretch(3, 2)
        layout.setStretch(4, 1)
        layout.setStretch(5, 1)
        frame.setLayout(layout)
        return diui 


    def showDialog(self, checked):
        self.window.setVisible(checked)


    def setupSystemTray(self):
        self.activateAction = QAction("Show", self.window)
        self.activateAction.setCheckable(True)
        self.activateAction.setChecked(True)
        self.activateAction.triggered.connect(self.showDialog)
        self.quitAction = QAction("Quit", self.window)
        self.quitAction.triggered.connect(self.closeEvent)
        self.trayIconMenu = QMenu(self.window)
        self.trayIconMenu.addAction(self.activateAction)
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QSystemTrayIcon(QIcon(":/images/icon.ico"), self.window)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.show()