#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program uses a RevPiCore to measure the time between two Input Events and writes the result in a CSV file

__author__ = "Heiner Buescher"

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import csv
import locale
import revpimodio2


class Ui_MainWindow(object):

    def __init__(self):
        self.rpi = revpimodio2.RevPiModIO(autorefresh=True)
        self.rpi.handlesignalend(self.cleanup_revpi)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("KnockOutMachine")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pictures = QtWidgets.QGraphicsView(self.centralwidget)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        self.pictures.setBackgroundBrush(brush)
        self.pictures.setObjectName("pictures")
        self.pictures.setGeometry(QtCore.QRect(700, 50, 700, 700))

        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setFixedSize(171, 51)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(99)
        self.startButton.setFont(font)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(lambda: self.onStartButtonClicked())

        self.highscoreButton = QtWidgets.QPushButton(self.centralwidget)
        self.highscoreButton.setFont(font)
        self.highscoreButton.setObjectName("highscoreButton")
        self.highscoreButton.setFixedSize(171, 51)
        self.highscoreButton.clicked.connect(lambda: self.onHighScoreButtonClicked())

        self.cancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setFixedSize(171, 51)
        self.cancelButton.clicked.connect(lambda: self.exitfunction())
        self.cancelButton.hide()

        self.lcdCounter = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdCounter.setEnabled(False)
        self.lcdCounter.setFixedSize(301, 151)
        self.lcdCounter.setSmallDecimalPoint(False)
        self.lcdCounter.setDigitCount(4)
        self.lcdCounter.setObjectName("lcdCounter")
        self.lcdCounter.hide()

        self.boxLayout = QtWidgets.QHBoxLayout()
        self.boxLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.boxLayout.addWidget(self.lcdCounter, alignment=QtCore.Qt.AlignHCenter)
        self.boxLayout.addWidget(self.startButton, alignment=QtCore.Qt.AlignHCenter)
        self.boxLayout.addWidget(self.highscoreButton, alignment=QtCore.Qt.AlignHCenter)
        self.boxLayout.addWidget(self.cancelButton)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.centralwidget.setLayout(self.boxLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("KnockOutMachine", "KnockOutMachine"))
        MainWindow.showMaximized()
        MainWindow.setStyleSheet("background-color: #006400;")

        self.startButton.setText(_translate("KnockOutMachine", "Messung starten"))
        self.startButton.setStyleSheet("background-color: white;")
        self.highscoreButton.setText(_translate("KnockOutMachine", "Bestenliste"))
        self.highscoreButton.setStyleSheet("background-color: white;")
        self.cancelButton.setText(_translate("KnockOutMachine", "Abbrechen"))
        self.cancelButton.setStyleSheet("background-color: white;")
        self.lcdCounter.setStyleSheet("background-color: white;")

    def exitfunction(self):
        self.rpi.device.exit()
        self.highscoreButton.show()
        self.startButton.show()

    # TODO add calculation
    def onStartButtonClicked(self):
        self.rpi.mainloop(blocking=False)
        self.lcdCounter.setEnabled(True)
        self.lcdCounter.show()
        self.cancelButton.show()
        self.startButton.hide()
        self.highscoreButton.hide()

        self.rpi.io.I_1.regevent(self.calculateTime)

        # newTime = input("Bitte Zeit eingeben: ")
        # inputName = str(input("Bitte Namen eingeben: "))
        # self.updateScores(inputName, newTime)

    # TODO show HighscoreList
    def onHighScoreButtonClicked(self):
        print("Dies ist eine Bestenliste")
        self.highscoreButton.hide()
        return None

    def calculateTime(self, ioname, iovalue):
        if iovalue == 0:
            self.timer.start()
            print("Timer startet!")
        else:
            self.timer.stop()
            print("Timer stopped!")

    def updateScores(self, inputName, newTime):
        locale.setlocale(locale.LC_ALL, '')
        DELIMITER = ';' if locale.localeconv()['decimal_point'] == ',' else ','
        row = [inputName, newTime]

        with open('timeList.csv', 'a', newline='') as timeFile:
            writer = csv.writer(timeFile, delimiter=DELIMITER)
            writer.writerow(row)

    # TODO add cleanup if necessary
    def cleanup_revpi(self):
        return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
