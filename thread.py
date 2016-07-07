from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import threading

class Communicate(QObject):
    signal = pyqtSignal(int, str)
    
class My_Gui(QWidget):
    def __init__(self):
        super().__init__()
        
        self.comm = Communicate()
        self.comm.signal.connect(self.append_data)
        self.initUI()
        self.ctr = 0
    
    def initUI(self):
        
        btn_count = QPushButton('Count')
        btn_count.clicked.connect(self.start_counting)
        self.te = QTextEdit()
        
        vbox = QVBoxLayout()
        vbox.addWidget(btn_count)
        vbox.addWidget(self.te)
        
        self.setLayout(vbox)
        self.setWindowTitle('MultiThreading in PyQT5')
        self.setGeometry(400, 400, 400, 400)
        self.show()
    
    def count(self, comm):
        i=101
        while(True):
            data = "Data "+str(i)
            comm.signal.emit(i, data)
            print("\r", self.ctr, end="")
            self.ctr+=1
        print()
    
    def start_counting(self):
        my_Thread = threading.Thread(target=self.count, args=(self.comm,))
        my_Thread.start()
    
    def append_data(self, num, data):
        self.te.append(str(num) + " " + data)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_gui = My_Gui()
    sys.exit(app.exec_())

