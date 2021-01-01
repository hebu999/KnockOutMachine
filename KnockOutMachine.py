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
        MainWindow.resize(1920, 1080)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pictures = QtWidgets.QGraphicsView(self.centralwidget)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        self.pictures.setBackgroundBrush(brush)
        self.pictures.setObjectName("pictures")
        self.pictures.setGeometry(QtCore.QRect(700, 50, 700, 700))

        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(370, 650, 171, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.startButton.setFont(font)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(lambda: self.onStartButtonClicked())

        self.highscoreButton = QtWidgets.QPushButton(self.centralwidget)
        self.highscoreButton.setGeometry(QtCore.QRect(300, 500, 171, 51))
        self.highscoreButton.setFont(font)
        self.highscoreButton.setObjectName("highscoreButton")
        self.highscoreButton.clicked.connect(lambda: self.onHighScoreButtonClicked())

        self.lcdCounter = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdCounter.setEnabled(False)
        self.lcdCounter.setGeometry(QtCore.QRect(320, 520, 251, 101))
        self.lcdCounter.setSmallDecimalPoint(False)
        self.lcdCounter.setDigitCount(4)
        self.lcdCounter.setObjectName("lcdCounter")
        self.lcdCounter.hide()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("KnockOutMachine", "KnockOutMachine"))
        self.startButton.setText(_translate("KnockOutMachine", "Messung starten"))
        self.highscoreButton.setText(_translate("KnockOutMachine", "Bestenliste"))

    def exitfunction(self):
        self.rpi.core.A1 = revpimodio2.OFF

    # TODO add calculation
    def onStartButtonClicked(self):
        self.rpi.mainloop()
        self.lcdCounter.setEnabled(True)
        self.lcdCounter.show()
        self.startButton.hide()

        self.rpi.io.I_1.regevent(self.timer.start())
        print("Timer startet!")

        self.rpi.io.I_1.regevent(self.timer.stop())
        print("Timer stopped!")

        # newTime = input("Bitte Zeit eingeben: ")
        # inputName = str(input("Bitte Namen eingeben: "))
        # self.updateScores(inputName, newTime)

    # TODO show HighscoreList
    def onHighScoreButtonClicked(self):
        print("Dies ist eine Bestenliste")
        self.highscoreButton.hide()
        return None

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
