#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program uses a RevPiCore to measure the time between two Input Events and writes the result in a CSV file

__author__ = "Heiner Buescher"

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import csv
import locale
import revpimodio2
import threading

Input_I1 = False


class Ui_MainWindow(object):

    def __init__(self):
        self.rpi = revpimodio2.RevPiModIO(autorefresh=True)
        self.rpi.handlesignalend(self.cleanup_revpi)
        self.rpi.io.I_1.reg_event(self.toggle_input, prefire=True)

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("KnockOutMachine")

        self.event = threading.Event()
        self.thread = threading.Thread(target=self.toggle_input)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pictures = QtWidgets.QLabel(self.centralwidget)
        self.pictures.setObjectName("pictures")
        self.pictures.setFixedSize(800, 800)
        self.pictures.setAlignment(QtCore.Qt.AlignCenter)
        self.pixmap = QtGui.QPixmap("J:\Downloads\Test\Logo-Button-Schuetzenverein_ohne-Rand.jpg")
        self.movie = QtGui.QMovie("J:\Downloads\Test\dog.gif")
        self.pictures.setPixmap(self.pixmap)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        mfont = QtGui.QFont("Times", 80, QtGui.QFont.Bold)
        self.messages = QtWidgets.QLineEdit(self.centralwidget)
        self.messages.setObjectName("messages")
        self.messages.setPalette(palette)
        self.messages.setFont(mfont)
        self.messages.setAlignment(QtCore.Qt.AlignCenter)
        self.messages.hide()

        self.model = QtGui.QStandardItemModel(self.centralwidget)
        self.model.setHorizontalHeaderLabels(['Name', 'Zeit in Sekunden'])
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.Qt.AlignJustify, QtCore.Qt.TextAlignmentRole)

        self.tableview = QtWidgets.QTableView(self.centralwidget)
        self.tableview.setObjectName("tableView")
        self.tableview.setFixedSize(250, 250)
        self.tableview.setModel(self.model)
        self.tableview.hide()

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(120)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setFixedSize(171, 51)
        self.startButton.setFont(font)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(lambda: self.on_start_button_clicked())

        self.highscoreButton = QtWidgets.QPushButton(self.centralwidget)
        self.highscoreButton.setFont(font)
        self.highscoreButton.setObjectName("highscoreButton")
        self.highscoreButton.setFixedSize(171, 51)
        self.highscoreButton.clicked.connect(lambda: self.on_high_score_button_clicked())

        self.cancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setFixedSize(171, 51)
        self.cancelButton.clicked.connect(lambda: self.exit_function())
        self.cancelButton.hide()

        self.lcdCounter = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdCounter.setEnabled(False)
        self.lcdCounter.setFixedSize(301, 151)
        self.lcdCounter.setSmallDecimalPoint(False)
        self.lcdCounter.setDigitCount(5)
        self.lcdCounter.setObjectName("lcdCounter")
        self.lcdCounter.display("00.00")
        self.lcdCounter.hide()
        self.runTime = ""
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)

        self.hboxPictures = QtWidgets.QHBoxLayout()
        self.hboxPictures.addWidget(self.pictures)
        self.hboxPictures.addWidget(self.messages)

        self.hboxButtons = QtWidgets.QHBoxLayout()
        self.hboxButtons.addWidget(self.lcdCounter)
        self.hboxButtons.addWidget(self.startButton)
        self.hboxButtons.addWidget(self.highscoreButton)
        self.hboxButtons.addWidget(self.cancelButton)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hboxPictures)
        self.vbox.addLayout(self.hboxButtons)

        self.centralwidget.setLayout(self.vbox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslate_ui(self, MainWindow):
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

    def on_start_button_clicked(self):
        self.lcdCounter.setEnabled(True)
        self.lcdCounter.show()
        self.cancelButton.show()
        self.startButton.hide()
        self.highscoreButton.hide()
        self.pictures.setMovie(self.movie)
        self.movie.start()
        self.rpi.mainloop(blocking=False)

        self.event.wait(1)
        self.start_timer()

    def on_high_score_button_clicked(self):
        DELIMITER = ';'
        self.highscoreButton.hide()
        self.startButton.hide()
        self.pictures.hide()
        self.tableview.show()

        with open('timeList.csv', 'r') as timeFile:
            for row in csv.reader(timeFile, delimiter=DELIMITER):
                times = [
                    QtGui.QStandardItem(field)
                    for field in row
                ]
                self.model.appendRow(times)

    def start_timer(self):
        self.messages.show()
        self.event.clear()
        self.thread.start()

        if not Input_I1:
            self.messages.setText("Bitte Glas vor Sensor stellen!")
            self.event.wait()
            self.event.clear()

        self.messages.setText("Bereit?")
        self.event.wait()

        self.messages.hide()
        self.now = 0
        self.update_timer()
        self.timer.timeout.connect(self.tick_timer)
        self.timer.start(10)
        self.timer.timeout.connect(self.stop_timer)
        print("Timer startet!")

    def stop_timer(self):
        # TODO Highscore only if time is in top ten
        if Input_I1:
            self.timer.stop()
            print("Die Zeit war: ", self.runTime)
            self.event.wait(5)

            # self.inputName, self.pressed = QtWidgets.QInputDialog.getText(self.centralwidget, 'Eingabe',
            #                                                               'Glückwunsch, bitte Namen eingeben:')
            # if self.pressed and self.inputName != '':
            #     self.update_scores(self.inputName, self.runTime)
            self.show_pictures(self.now)
            self.exit_function()

    def toggle_input(self, ioname, iovalue):
        global Input_I1
        Input_I1 = iovalue
        self.event.set()

    def update_timer(self):
        self.runTime = "%02d.%02d" % (self.now / 100, self.now % 100)
        self.lcdCounter.display(self.runTime)

    def tick_timer(self):
        self.now += 1
        self.update_timer()

    def update_scores(self, inputName, runTime):
        # TODO highscore limit of ten? needs to be clarified
        locale.setlocale(locale.LC_ALL, '')
        DELIMITER = ';' if locale.localeconv()['decimal_point'] == ',' else ','
        row = [inputName, runTime]

        with open('timeList.csv', 'a', newline='') as timeFile:
            writer = csv.writer(timeFile, delimiter=DELIMITER)
            writer.writerow(row)

    def show_pictures(self, runTime):
        if runTime <= 100:
            self.pixmap = QtGui.QPixmap(".jpg")
            self.pictures.setPixmap(self.pixmap)
        elif runTime <= 300:
            self.pixmap = QtGui.QPixmap(".jpg")
            self.pictures.setPixmap(self.pixmap)
        elif runTime <= 600:
            self.pixmap = QtGui.QPixmap(".jpg")
            self.pictures.setPixmap(self.pixmap)
        else:
            self.pixmap = QtGui.QPixmap(".jpg")
            self.pictures.setPixmap(self.pixmap)

    def exit_function(self):
        self.rpi.exit(full=False)
        self.timer.stop()
        self.lcdCounter.hide()
        self.highscoreButton.show()
        self.startButton.show()
        self.cancelButton.hide()

    # TODO add cleanup if necessary
    def cleanup_revpi(self):
        return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setup_ui(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
