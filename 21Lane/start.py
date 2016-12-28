#!/usr/bin/python3 

from PyQt5.QtWidgets import QApplication, QWidget
import resources_rc
import app, sys

if __name__=="__main__":
    if not ((sys.version_info.major == 3) and \
        (sys.version_info.minor >= 5)):
        print ("Sorry. PyQt5 requires at least Python3.5")
        sys.exit()
    q = QApplication([])
    q.setStyle("fusion")
    window = QWidget()
    print (QApplication.style())
    u = app.GUI(window)
    sys.exit(q.exec_())
