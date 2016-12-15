# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'downloaditem.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(485, 68)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.filenameLbl = QtWidgets.QLabel(Form)
        self.filenameLbl.setObjectName("filenameLbl")
        self.gridLayout.addWidget(self.filenameLbl, 0, 0, 1, 2)
        self.progressLbl = QtWidgets.QLabel(Form)
        self.progressLbl.setObjectName("progressLbl")
        self.gridLayout.addWidget(self.progressLbl, 0, 2, 1, 1)
        self.options = QtWidgets.QToolButton(Form)
        self.options.setObjectName("options")
        self.gridLayout.addWidget(self.options, 0, 3, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 1, 1, 1, 3)
        self.serverName = QtWidgets.QLabel(Form)
        self.serverName.setStyleSheet("color: rgb(85, 0, 255);\n"
"text-decoration: underline;")
        self.serverName.setObjectName("serverName")
        self.gridLayout.addWidget(self.serverName, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.filenameLbl.setText(_translate("Form", "This is my file name"))
        self.progressLbl.setText(_translate("Form", "completion"))
        self.options.setText(_translate("Form", "..."))
        self.serverName.setText(_translate("Form", "gangsters"))

