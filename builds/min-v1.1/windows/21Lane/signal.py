import sys
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
import threading, time


class Communicate(QObject):
    
    closeApp = pyqtSignal() 

def mythread(btn):
    while True:
        time.sleep(3)
        btn.click()
        print("Click from the heart")

    

class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        
    def initUI(self):      

        self.c = Communicate()
        self.c.closeApp.connect(self.displayMessage)      

        btn = QPushButton(self) 
        btn.setText("Click me")
        btn.clicked.connect(self.emitSignal)
        
        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Emit signal')

        th = threading.Thread(target=mythread, args=(btn,))
        th.start()
        self.show()
        
    def displayMessage(self):
        print(self.sender())
        print("You clicked me!")
        
    def emitSignal(self, event):
        
        self.c.closeApp.emit()
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())