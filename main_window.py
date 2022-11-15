import datetime as dt

from time import sleep
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap
from main_window_ui import Ui_MainWindow
from diary import *
from schedule import *
from grades import *

# ---------------------------------------------------------------------------------
# class Time_updater_Thread.
# Создание 2 потока для асинхронной работы часов.
# acyncio тут не подходит, т.к. цикл событий asyncio останавливает цикл событий Qt.
# ---------------------------------------------------------------------------------

class Time_updater_Thread(QThread):
    def __init__(self, mainwindow, parent=None):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        while True:
            MainWindow.upd_time(self.mainwindow)
            sleep(1)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Электронный дневник Ver. 1.0')

        self.time_upd = Time_updater_Thread(mainwindow=self)
        self.time_upd.start()

        self.diary = Diary()
        self.schedule = Schedule()
        self.grades = Grades()

        self.initobjs()
        self.upd_date()

    def initobjs(self):
        self.img = QLabel(self)
        self.img.setPixmap(QPixmap('picture.png'))
        self.img.setGeometry(141, 240, 64, 64)
        self.open_diary_btn.clicked.connect(self.open_diary)
        self.open_schedule_btn.clicked.connect(self.open_schedule)
        self.open_grades_btn.clicked.connect(self.open_grades_table)

    def open_diary(self):
        self.diary.show()

    def open_schedule(self):
        self.schedule.show()
    
    def open_grades_table(self):
        self.grades.show()

    def upd_time(self):
        self.time_now.setText(
            'Время: ' + dt.datetime.now().strftime('%H:%M:%S'))

    def upd_date(self):
        self.date_now.setText('Сегодня ' + WEEK_DAYS[dt.datetime.now().strftime(
            '%A')][0] + ', ' + dt.datetime.now().strftime('%d.%m.%y'))
