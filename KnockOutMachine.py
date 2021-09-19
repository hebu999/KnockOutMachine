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
        self.messages.setReadOnly(True)
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

        self.input_window = QtWidgets.QWidget()
        self.input_window.setWindowTitle("Bitte Namen eingeben")
        self.input_window.resize(300, 100)
        self.input_window.move(850, 820)
        # self.input_window.setWindowFlags(
        #     QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.input_layout = QtWidgets.QFormLayout()

        self.input_dialogue = QtWidgets.QLineEdit(self.centralwidget)
        self.input_dialogue.setMaxLength(30)

        buttonFont = QtGui.QFont("Times", 16, QtGui.QFont.Bold)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setFixedSize(191, 71)
        self.startButton.setFont(buttonFont)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(lambda: self.on_start_button_clicked())

        self.inputButton = QtWidgets.QPushButton(self.centralwidget)
        self.inputButton.setObjectName("inputButton")
        self.inputButton.resize(self.inputButton.sizeHint())
        self.inputButton.setDisabled(True)

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

        self.cancelTimerButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelTimerButton.setFont(buttonFont)
        self.cancelTimerButton.setObjectName("cancelTimerButton")
        self.cancelTimerButton.setFixedSize(191, 71)
        self.cancelTimerButton.clicked.connect(lambda: self.exit_timer_function())
        self.cancelTimerButton.hide()

        self.cancelScoreButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelScoreButton.setFont(buttonFont)
        self.cancelScoreButton.setObjectName("cancelScoreButton")
        self.cancelScoreButton.setFixedSize(191, 71)
        self.cancelScoreButton.clicked.connect(lambda: self.exit_score_function())
        self.cancelScoreButton.hide()

        self.lcdCounter = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdCounter.setEnabled(False)
        self.lcdPalette = self.lcdCounter.palette()
        self.lcdCounter.setFixedSize(1350, 750)
        self.lcdCounter.setSmallDecimalPoint(False)
        self.lcdCounter.setDigitCount(5)
        self.lcdCounter.setObjectName("lcdCounter")
        self.lcdCounter.display("00.00")
        self.lcdCounter.hide()
        self.runTime = ""

        self.timer, self.glass_not_set_timer, self.glass_set_timer = QtCore.QTimer(), QtCore.QTimer(), QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick_timer)
        self.timer.timeout.connect(self.stop_timer)

        self.glass_set_timer.setSingleShot(True)
        self.glass_set_timer.setInterval(100)
        self.glass_set_timer.timeout.connect(self.glass_set)

        self.glass_not_set_timer.setSingleShot(True)
        self.glass_not_set_timer.setInterval(100)
        self.glass_not_set_timer.timeout.connect(self.glass_not_set)

        self.gridPictures = QtWidgets.QGridLayout()
        self.gridPictures.addWidget(self.lcdCounter, 1, 1, QtCore.Qt.AlignCenter)
        self.gridPictures.addWidget(self.messages, 2, 1, QtCore.Qt.AlignCenter)
        self.gridPictures.addWidget(self.pictures, 3, 1, QtCore.Qt.AlignCenter)
        self.gridPictures.addWidget(self.tableview, 0, QtCore.Qt.AlignCenter)

        self.hboxButtons = QtWidgets.QHBoxLayout()
        self.hboxButtons.addWidget(self.startButton)
        self.hboxButtons.addWidget(self.toggleButton)
        self.hboxButtons.addWidget(self.highscoreButton)
        self.hboxButtons.addWidget(self.cancelTimerButton)
        self.hboxButtons.addWidget(self.cancelScoreButton)

        self.input_layout.addRow("", self.input_dialogue)
        self.input_layout.addRow("", self.inputButton)
        self.input_window.setLayout(self.input_layout)

        # TODO set correct layout span and stretch
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.gridPictures)
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hboxButtons)
        self.vbox.addStretch(3)

        self.input_dialogue.textChanged.connect(self.enable_input_button)
        self.input_dialogue.returnPressed.connect(self.inputButton.click)
        self.inputButton.clicked.connect(lambda: self.update_scores(self.input_dialogue.text(), self.runTime))
        self.inputButton.clicked.connect(lambda: self.input_window.close())
        self.inputButton.clicked.connect(lambda: self.exit_timer_function())
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
        self.inputButton.setText(_translate("KnockOutMachine", "Eingabe bestätigen"))
        self.messages.setStyleSheet("border: none;")
        self.toggleButton.setText(_translate("KnockOutMachine", "Toggle Input"))
        self.toggleButton.setStyleSheet("background-color: white;")
        self.highscoreButton.setText(_translate("KnockOutMachine", "Bestenliste"))
        self.highscoreButton.setStyleSheet("background-color: white;")
        # self.cancelButton.setText(_translate("KnockOutMachine", "Abbrechen"))
        self.cancelTimerButton.setIcon(QtGui.QIcon("display/cancel_button.png"))
        self.cancelTimerButton.setIconSize(QtCore.QSize(50, 50))
        self.cancelTimerButton.setStyleSheet("background-color: white;")
        self.cancelScoreButton.setIcon(QtGui.QIcon("display/cancel_button.png"))
        self.cancelScoreButton.setIconSize(QtCore.QSize(50, 50))
        self.cancelScoreButton.setStyleSheet("background-color: white;")
        self.lcdCounter.setStyleSheet("background-color: #113f0c;")
        self.lcdCounter.setStyleSheet("color: white;")
        self.tableview.setStyleSheet("background-color: white;")

    def enable_input_button(self):
        if len(self.input_dialogue.text()) > 0:
            self.inputButton.setDisabled(False)
        else:
            self.inputButton.setDisabled(True)

    def on_start_button_clicked(self):
        self.lcdCounter.display("00.00")
        self.movie = QtGui.QMovie("display/dog.gif")
        self.lcdCounter.setEnabled(True)
        self.lcdCounter.show()
        self.cancelTimerButton.show()
        self.toggleButton.show()
        self.startButton.hide()
        self.highscoreButton.hide()
        self.pictures.hide()

        if Input_I1:
            self.glass_not_set()
        else:
            self.glass_set()

    def on_high_score_button_clicked(self):
        self.highscoreButton.hide()
        self.startButton.setDisabled(True)
        self.startButton.hide()
        self.pictures.hide()
        self.cancelScoreButton.show()
        self.tableview.show()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Name', 'Zeit in Sekunden'])
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.Qt.AlignJustify, QtCore.Qt.TextAlignmentRole)
        self.delimiter = ';'

        try:
            with open('timeList.csv', 'r') as timeFile:
                reader = csv.reader(timeFile, delimiter=self.delimiter)
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

    def glass_not_set(self):
        self.glass_not_set_timer.start()
        self.messages.show()
        self.messages.setText("Bitte Glas vor Sensor stellen!")
        if not Input_I1:
            self.glass_not_set_timer.stop()
            self.glass_set()

    def glass_set(self):
        self.glass_set_timer.start()
        self.messages.show()
        self.messages.setText("Glas erkannt, wenn bereit los!")
        if Input_I1:
            self.glass_set_timer.stop()
            self.movie.start()
            self.start_timer()

    def start_timer(self):
        self.messages.hide()
        # self.pictures.show()
        # self.pictures.setMovie(self.movie)

        self.now = 0
        self.update_timer()
        self.timer.start(10)

    def stop_timer(self):
        if not Input_I1:
            self.timer.stop()

        if not self.timer.isActive():
            # self.show_pictures(self.now)
            self.input_window.show()

    def toggle_input(self):
        global Input_I1
        Input_I1 = not Input_I1

    def update_timer(self):
        self.runTime = "%02d.%02d" % (self.now / 100, self.now % 100)
        self.lcdCounter.display(self.runTime)
        if self.now / 100 == 99:
            self.exit_timer_function()

    def tick_timer(self):
        self.now += 1
        self.update_timer()

    def update_scores(self, inputName, runTime):
        self.datetime = QtCore.QDateTime.currentDateTime()
        self.delimiter = ';'
        row = [inputName, runTime.replace(".", ","), self.datetime.toString(QtCore.Qt.DefaultLocaleShortDate)]

        with open('timeList.csv', 'a', newline='') as timeFile:
            writer = csv.writer(timeFile, delimiter=self.delimiter)
            writer.writerow(row)
        self.input_dialogue.clear()

    def play_sound(self, fileName):
        self.filename = "home/heiner/PyCharmProjects/KnockOutMachine/sounds/" + fileName
        self.url = QtCore.QUrl.fromLocalFile(self.filename)
        self.content = QtMultimedia.QMediaContent(self.url)
        self.player.setMedia(self.content)
        self.player.play()

    def show_pictures(self, runTime):
        if runTime <= 200:
            self.rand = randint(0, 2)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display/Trump.gif")
            else:
                self.movie = QtGui.QMovie("display/dog.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("cheering.mp3")

        elif runTime <= 500:
            self.rand = randint(0, 6)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display/1.webp")
            elif self.case(2):
                self.movie = QtGui.QMovie("display/2.gif")
            elif self.case(3):
                self.movie = QtGui.QMovie("display/3.gif")
            elif self.case(4):
                self.movie = QtGui.QMovie("display/4.gif")
            elif self.case(5):
                self.movie = QtGui.QMovie("display/5.gif")
            else:
                self.movie = QtGui.QMovie("display/6.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("applause-2.mp3")

        elif runTime <= 800:
            self.rand = randint(0, 2)
            self.case = lambda x: self.rand < x
            if self.case(1):
                self.movie = QtGui.QMovie("display/Bier2.gif")
            else:
                self.movie = QtGui.QMovie("display/1.webp")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("laughter-2.mp3")

        else:
            self.movie = QtGui.QMovie("display/dog.gif")
            self.movie.start()
            self.pictures.setMovie(self.movie)
            self.play_sound("laughter-2.mp3")

    def exit_score_function(self):
        self.tableview.hide()
        self.toggleButton.hide()
        self.cancelScoreButton.hide()
        self.highscoreButton.show()
        self.startButton.setEnabled(True)
        self.startButton.show()
        self.pictures.show()

        self.pixmap = QtGui.QPixmap("display/main_menu.png")
        self.pictures.setPixmap(self.scaledPixmap)

    def exit_timer_function(self):
        # self.rpi.exit(full=False)
        self.timer.stop()
        self.glass_set_timer.stop()
        self.glass_not_set_timer.stop()
        self.player.stop()
        self.lcdCounter.setEnabled(False)
        self.lcdCounter.hide()
        self.tableview.hide()
        self.toggleButton.hide()
        self.cancelTimerButton.hide()
        self.messages.hide()
        self.highscoreButton.show()
        self.startButton.setEnabled(True)
        self.startButton.show()
        self.pictures.show()

        self.pixmap = QtGui.QPixmap("display/main_menu.png")
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
