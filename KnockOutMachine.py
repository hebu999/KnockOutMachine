#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program uses a RevPiCore to measure the time between two Input Events and writes the result in a CSV file

__author__ = "Heiner Buescher"

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from random import randint
import sys
import csv
import locale
import revpimodio2

Input_I1 = True


class Ui_MainWindow(object):

    # def __init__(self):
    #     self.rpi = revpimodio2.RevPiModIO(autorefresh=True)
    #     self.rpi.handlesignalend(self.cleanup_revpi)
    #     self.rpi.io.I_1.reg_event(self.toggle_input, prefire=True)

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("KnockOutMachine")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pictures = QtWidgets.QLabel(self.centralwidget)
        self.pictures.setObjectName("pictures")
        self.pictures.setFixedSize(800, 800)
        self.pictures.setAlignment(QtCore.Qt.AlignCenter)
        self.pixmap = QtGui.QPixmap("display\\Logo-Button-Schuetzenverein.jpg")
        self.pictures.setPixmap(self.pixmap)
        self.player = QtMultimedia.QMediaPlayer()

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

        tableFont = QtGui.QFont("Times", 16)
        self.tableview = QtWidgets.QTableView(self.centralwidget)
        self.tableview.setObjectName("tableView")
        self.tableview.setFixedSize(480, 900)
        self.tableview.verticalHeader().setDefaultSectionSize(85)
        self.tableview.horizontalHeader().setDefaultSectionSize(200)
        self.tableview.setFont(tableFont)
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

        self.toggleButton = QtWidgets.QPushButton(self.centralwidget)
        self.toggleButton.setFixedSize(171, 51)
        self.toggleButton.setFont(font)
        self.toggleButton.setObjectName("toggleButton")
        self.toggleButton.clicked.connect(lambda: self.toggle_input())
        self.toggleButton.hide()

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

        self.timer, self.glas_not_set_timer, self.glas_set_timer = QtCore.QTimer(), QtCore.QTimer(), QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick_timer)
        self.timer.timeout.connect(self.stop_timer)

        self.glas_set_timer.setSingleShot(True)
        self.glas_set_timer.setInterval(100)
        self.glas_set_timer.timeout.connect(self.glas_set)

        self.glas_not_set_timer.setSingleShot(True)
        self.glas_not_set_timer.setInterval(100)
        self.glas_not_set_timer.timeout.connect(self.glas_not_set)

        self.hboxPictures = QtWidgets.QHBoxLayout()
        self.hboxPictures.addWidget(self.pictures)
        self.hboxPictures.addWidget(self.messages)
        self.hboxPictures.addWidget(self.tableview)

        self.hboxButtons = QtWidgets.QHBoxLayout()
        self.hboxButtons.addWidget(self.lcdCounter)
        self.hboxButtons.addWidget(self.startButton)
        self.hboxButtons.addWidget(self.toggleButton)
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

        locale.setlocale(locale.LC_ALL, '')

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("KnockOutMachine", "KnockOutMachine"))
        MainWindow.showMaximized()
        MainWindow.setStyleSheet("background-color: #113f0c;")

        self.startButton.setText(_translate("KnockOutMachine", "Messung starten"))
        self.startButton.setStyleSheet("background-color: white;")
        self.toggleButton.setText(_translate("KnockOutMachine", "Toggle Input"))
        self.toggleButton.setStyleSheet("background-color: white;")
        self.highscoreButton.setText(_translate("KnockOutMachine", "Bestenliste"))
        self.highscoreButton.setStyleSheet("background-color: white;")
        self.cancelButton.setText(_translate("KnockOutMachine", "Abbrechen"))
        self.cancelButton.setStyleSheet("background-color: white;")
        self.lcdCounter.setStyleSheet("background-color: white;")
        self.tableview.setStyleSheet("background-color: white;")

    def on_start_button_clicked(self):
        self.lcdCounter.display("00.00")
        self.movie = QtGui.QMovie("display\Bier.webp")
        self.lcdCounter.setEnabled(True)
        self.lcdCounter.show()
        self.cancelButton.show()
        self.toggleButton.show()
        self.startButton.hide()
        self.highscoreButton.hide()
        self.pictures.hide()

        if not Input_I1:
            self.glas_not_set()
        else:
            self.glas_set()

    def on_high_score_button_clicked(self):
        self.highscoreButton.hide()
        self.startButton.hide()
        self.pictures.hide()
        self.cancelButton.show()
        self.tableview.show()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Name', 'Zeit in Sekunden'])
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.Qt.AlignJustify, QtCore.Qt.TextAlignmentRole)

        DELIMITER = ';' if locale.localeconv()['decimal_point'] == ',' else ','

        try:
            with open('timeList.csv', 'r') as timeFile:
                reader = csv.reader(timeFile, delimiter=DELIMITER)
                reader = [[x.replace(',', '.') for x in l] for l in reader]
                highscore_list_sorted = sorted(reader, key=lambda x: float(x[1]))[:10]

                for row in highscore_list_sorted:
                    times = [
                        QtGui.QStandardItem(field.replace(".", ","))
                        for field in row
                    ]
                    self.model.appendRow(times)
        except FileNotFoundError:
            print("Timelist File does not exist")

    def glas_not_set(self):
        self.glas_not_set_timer.start()
        self.messages.show()
        self.messages.setText("Bitte Glas vor Sensor stellen!")
        if Input_I1:
            self.glas_not_set_timer.stop()
            self.glas_set()

    def glas_set(self):
        self.glas_set_timer.start()
        self.messages.show()
        self.messages.setText("Bereit?")
        if not Input_I1:
            self.glas_set_timer.stop()
            self.movie.start()
            self.start_timer()

    def start_timer(self):
        self.messages.hide()
        self.pictures.show()
        self.pictures.setMovie(self.movie)

        self.now = 0
        self.update_timer()
        self.timer.start(10)

    def stop_timer(self):
        if Input_I1:
            self.timer.stop()

        if not self.timer.isActive():
            self.show_pictures(self.now)

            self.inputName, self.pressed = QtWidgets.QInputDialog.getText(self.centralwidget, 'Eingabe',
                                                                          'Bitte Namen eingeben:')
            if self.pressed and self.inputName != '':
                self.update_scores(self.inputName, self.runTime)
            self.exit_function()

    def toggle_input(self):
        global Input_I1
        Input_I1 = not Input_I1

    def update_timer(self):
        self.runTime = "%02d.%02d" % (self.now / 100, self.now % 100)
        self.lcdCounter.display(self.runTime)
        if self.now / 100 == 99:
            self.exit_function()

    def tick_timer(self):
        self.now += 1
        self.update_timer()

    def update_scores(self, inputName, runTime):
        DELIMITER = ';' if locale.localeconv()['decimal_point'] == ',' else ','
        row = [inputName, runTime.replace(".", ",")]

        with open('timeList.csv', 'a', newline='') as timeFile:
            writer = csv.writer(timeFile, delimiter=DELIMITER)
            writer.writerow(row)

    def play_sound(self, fileName):
        self.filename = "sounds\\" + fileName
        self.url = QtCore.QUrl.fromLocalFile(self.filename)
        self.content = QtMultimedia.QMediaContent(self.url)
        self.player.setMedia(self.content)
        self.player.play()

    def show_pictures(self, runTime):
        if runTime <= 200:
            self.rand = randint(0, 2)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display\\Trump.gif")
            else:
                self.movie = QtGui.QMovie("display\\dog.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("example.mp3")

        elif runTime <= 500:
            self.rand = randint(0, 6)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display\\1.webp")
            elif self.case(2):
                self.movie = QtGui.QMovie("display\\2.gif")
            elif self.case(3):
                self.movie = QtGui.QMovie("display\\3.gif")
            elif self.case(4):
                self.movie = QtGui.QMovie("display\\4.gif")
            elif self.case(5):
                self.movie = QtGui.QMovie("display\\5.gif")
            else:
                self.movie = QtGui.QMovie("display\\6.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("example.mp3")

        elif runTime <= 800:
            self.rand = randint(0, 2)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display\\Bier2.gif")
            else:
                self.movie = QtGui.QMovie("display\\1.webp")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("example.mp3")

        else:
            self.movie = QtGui.QMovie("display\\dog.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("example.mp3")

    def exit_function(self):
        # self.rpi.exit(full=False)
        self.timer.stop()
        self.glas_set_timer.stop()
        self.glas_not_set_timer.stop()
        self.player.stop()
        self.lcdCounter.hide()
        self.tableview.hide()
        self.toggleButton.hide()
        self.cancelButton.hide()
        self.messages.hide()
        self.highscoreButton.show()
        self.startButton.show()
        self.pictures.show()

        self.pixmap = QtGui.QPixmap("display\\Logo-Button-Schuetzenverein.jpg")
        self.pictures.setPixmap(self.pixmap)

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
