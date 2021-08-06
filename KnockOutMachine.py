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

Input_I1 = False


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
        self.pictures.setFixedSize(900, 853)
        self.pixmap = QtGui.QPixmap("display/main_menu.png")
        self.scaledPixmap = self.pixmap.scaled(900, 900, QtCore.Qt.KeepAspectRatio)
        self.pictures.setPixmap(self.scaledPixmap)
        self.player = QtMultimedia.QMediaPlayer()

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        mfont = QtGui.QFont("Times", 80, QtGui.QFont.Bold)
        self.messages = QtWidgets.QLineEdit(self.centralwidget)
        self.messages.setObjectName("messages")
        self.messages.setPalette(palette)
        self.messages.setFont(mfont)
        self.messages.setAlignment(QtCore.Qt.AlignCenter)
        self.messages.setFixedSize(1400, 200)
        self.messages.hide()

        self.model = QtGui.QStandardItemModel(self.centralwidget)
        tableFont = QtGui.QFont("Times", 16)
        self.tableview = QtWidgets.QTableView(self.centralwidget)
        self.tableview.setObjectName("tableView")
        self.tableview.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableview.setMaximumWidth(500)
        self.tableview.setMaximumHeight(900)
        self.tableview.verticalHeader().setDefaultSectionSize(85)
        self.tableview.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableview.setFont(tableFont)
        self.tableview.setModel(self.model)
        self.tableview.hide()

        buttonFont = QtGui.QFont("Times", 16, QtGui.QFont.Bold)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setFixedSize(191, 71)
        self.startButton.setFont(buttonFont)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(lambda: self.on_start_button_clicked())

        self.input_dialogue = QtWidgets.QInputDialog(self.centralwidget)
        self.input_dialogue.setInputMode(QtWidgets.QInputDialog.TextInput)
        self.input_dialogue.resize(self.input_dialogue.sizeHint())
        self.input_dialogue.setWindowTitle("Namenseingabe")
        self.input_dialogue.setLabelText("Bitte Namen eingeben:")

        self.toggleButton = QtWidgets.QPushButton(self.centralwidget)
        self.toggleButton.setFixedSize(191, 71)
        self.toggleButton.setFont(buttonFont)
        self.toggleButton.setObjectName("toggleButton")
        self.toggleButton.clicked.connect(lambda: self.toggle_input())
        self.toggleButton.hide()

        self.highscoreButton = QtWidgets.QPushButton(self.centralwidget)
        self.highscoreButton.setFont(buttonFont)
        self.highscoreButton.setObjectName("highscoreButton")
        self.highscoreButton.setFixedSize(191, 71)
        self.highscoreButton.clicked.connect(lambda: self.on_high_score_button_clicked())

        self.cancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelButton.setFont(buttonFont)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setFixedSize(191, 71)
        self.cancelButton.clicked.connect(lambda: self.exit_function())
        self.cancelButton.hide()

        self.lcdCounter = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdCounter.setEnabled(False)
        self.lcdCounter.setFixedSize(1050, 450)
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

        self.gridPictures = QtWidgets.QGridLayout()
        self.gridPictures.addWidget(self.lcdCounter, 1, 1, QtCore.Qt.AlignCenter)
        self.gridPictures.addWidget(self.messages, 2, 1, QtCore.Qt.AlignCenter)
        self.gridPictures.addWidget(self.pictures, 3, 1, QtCore.Qt.AlignCenter)
        self.gridPictures.addWidget(self.tableview, 0, QtCore.Qt.AlignCenter)

        self.hboxButtons = QtWidgets.QHBoxLayout()
        self.hboxButtons.addWidget(self.startButton)
        self.hboxButtons.addWidget(self.toggleButton)
        self.hboxButtons.addWidget(self.highscoreButton)
        self.hboxButtons.addWidget(self.cancelButton, QtCore.Qt.AlignRight)

        # TODO set correct layout span and stretch
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.gridPictures)
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hboxButtons)
        self.vbox.addStretch(3)

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
        MainWindow.showFullScreen()
        MainWindow.setStyleSheet("background-color: #113f0c;")

        self.startButton.setText(_translate("KnockOutMachine", "Messung starten"))
        self.startButton.setStyleSheet("background-color: white;")
        self.input_dialogue.setStyleSheet("background-color: white;")
        self.toggleButton.setText(_translate("KnockOutMachine", "Toggle Input"))
        self.toggleButton.setStyleSheet("background-color: white;")
        self.highscoreButton.setText(_translate("KnockOutMachine", "Bestenliste"))
        self.highscoreButton.setStyleSheet("background-color: white;")
        self.cancelButton.setText(_translate("KnockOutMachine", "Abbrechen"))
        self.cancelButton.setIcon(QtGui.QIcon("display/cancel_button.png"))
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
                    self.tableview.setColumnHidden(2, True)
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
            self.pressed = self.input_dialogue.exec_()
            self.inputName = self.input_dialogue.textValue()

            if self.pressed and self.inputName != '':
                self.update_scores(self.inputName, self.runTime)
                self.input_dialogue.clearMask()
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
        self.datetime = QtCore.QDateTime.currentDateTime()
        DELIMITER = ';' if locale.localeconv()['decimal_point'] == ',' else ','
        row = [inputName, runTime.replace(".", ","), self.datetime.toString(QtCore.Qt.DefaultLocaleShortDate)]

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
            self.play_sound("applause-2.mp3")

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
            self.play_sound("applause-8.mp3")

        elif runTime <= 800:
            self.rand = randint(0, 2)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display\\Bier2.gif")
            else:
                self.movie = QtGui.QMovie("display\\1.webp")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("laughter-2.mp3")

        else:
            self.movie = QtGui.QMovie("display\\dog.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("laughter-2.mp3")

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

        self.pixmap = QtGui.QPixmap("display\\main_menu.png")
        self.pictures.setPixmap(self.scaledPixmap)

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
