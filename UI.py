# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(200, 80, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(330, 120, 401, 211))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView_2 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_2.setGeometry(QtCore.QRect(330, 350, 401, 192))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.comboBox_SerialPorts = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_SerialPorts.setGeometry(QtCore.QRect(20, 60, 71, 21))
        self.comboBox_SerialPorts.setObjectName("comboBox_SerialPorts")
        self.pushButton_UpdatePorts = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_UpdatePorts.setGeometry(QtCore.QRect(20, 10, 75, 23))
        self.pushButton_UpdatePorts.setObjectName("pushButton_UpdatePorts")
        self.comboBox_Baudrate = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_Baudrate.setGeometry(QtCore.QRect(20, 110, 69, 22))
        self.comboBox_Baudrate.setObjectName("comboBox_Baudrate")
        self.comboBox_Baudrate.addItem("")
        self.comboBox_Baudrate.addItem("")
        self.pushButton_StartProgram = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_StartProgram.setGeometry(QtCore.QRect(120, 260, 75, 23))
        self.pushButton_StartProgram.setObjectName("pushButton_StartProgram")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 40, 51, 16))
        self.label_2.setObjectName("label_2")
        self.label_41 = QtWidgets.QLabel(self.centralwidget)
        self.label_41.setGeometry(QtCore.QRect(30, 90, 51, 16))
        self.label_41.setObjectName("label_41")
        self.label_35 = QtWidgets.QLabel(self.centralwidget)
        self.label_35.setGeometry(QtCore.QRect(130, 10, 91, 16))
        self.label_35.setObjectName("label_35")
        self.doubleSpinBox_UpdateTime = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_UpdateTime.setGeometry(QtCore.QRect(130, 30, 62, 22))
        self.doubleSpinBox_UpdateTime.setDecimals(3)
        self.doubleSpinBox_UpdateTime.setProperty("value", 0.01)
        self.doubleSpinBox_UpdateTime.setObjectName("doubleSpinBox_UpdateTime")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "sdsfdf"))
        self.pushButton_UpdatePorts.setText(_translate("MainWindow", "Update Ports"))
        self.comboBox_Baudrate.setItemText(0, _translate("MainWindow", "9600"))
        self.comboBox_Baudrate.setItemText(1, _translate("MainWindow", "115200"))
        self.pushButton_StartProgram.setText(_translate("MainWindow", "Start Program"))
        self.label_2.setText(_translate("MainWindow", "Serial Port"))
        self.label_41.setText(_translate("MainWindow", "Baud Rate"))
        self.label_35.setText(_translate("MainWindow", "Update Time [s]"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

