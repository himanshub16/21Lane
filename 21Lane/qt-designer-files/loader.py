import sys
from PyQt5.QtWidgets import QApplication, QDialog
import dialog

app = QApplication([])
di = dialog.Ui_Dialog()
d = QDialog()
di.setupUi(d)
d.show()
sys.exit(app.exec_())
