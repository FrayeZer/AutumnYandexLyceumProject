import sqlite3
import datetime as dt

from PyQt5.QtWidgets import *
from diary_ui import Ui_Diary
from schedule import WEEK_DAYS, EXECUTE_LESSONS, WEEK_DAYS_INDEXES


MONTHS = {
    '0': 'Январь',
    '1': 'Февраль',
    '2': 'Март',
    '3': 'Апрель',
    '4': 'Май',
    '5': 'Июнь',
    '6': 'Июль',
    '7': 'Август',
    '8': 'Сентябрь',
    '9': 'Октябрь',
    '10': 'Ноябрь',
    '11': 'Декабрь'
}


class Diary(QMainWindow, Ui_Diary):
    def __init__(self) -> None:
        super(Diary, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Дневник')

        # Получаю объект класса datetime, в котором находятся данные о ближайшем
        # прошедшем понедельнике. Понедельник - начала отсчета недели, все данные
        # заполняется относительно него, поэтому он нужен.
        self.monday_day = dt.datetime.now()
        while self.monday_day.strftime('%A') != 'Monday':
            self.monday_day = self.monday_day - dt.timedelta(days=1)

        self.all_tables = (self.monday_table, self.tuesday_table, self.wednesday_table,
                           self.thursday_table, self.friday_table, self.saturday_table)

        self.get_monday_info()
        self.initobjs()

    def initobjs(self):
        self.next_week.clicked.connect(self.next)
        self.previous_week.clicked.connect(self.previous)
        self.update_diary_btn.clicked.connect(self.update_button_pressed)
        self.save_diary_btn.clicked.connect(self.save_button_pressed)

        self.diary_updater()

    def next(self):
        self.monday_day = self.monday_day + dt.timedelta(days=7)
        self.diary_updater()

    def previous(self):
        self.monday_day = self.monday_day - dt.timedelta(days=7)
        self.diary_updater()

    def update_button_pressed(self):
        self.diary_updater()

    def save_button_pressed(self):
        self.save_diary()

    def diary_updater(self):
        self.get_monday_info()
        # ...
        self.update_labels()
        self.update_all_tables_and_insert_to_sql()

    def update_all_tables_and_insert_to_sql(self):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()

        for i, table in enumerate(self.all_tables):
            self.get_lessons_lst(WEEK_DAYS_INDEXES[str(i)])
            table.setRowCount(self.lsns_count)
            for j in range(self.lsns_count):
                table.setItem(j, 0, QTableWidgetItem(
                    self.lssn_lst_from_sql[j]))
                table.setItem(j, 1, QTableWidgetItem(
                    self.get_stats(i, self.lssn_lst_from_sql[j])[0]))
                table.setItem(j, 2, QTableWidgetItem(
                    self.get_stats(i, self.lssn_lst_from_sql[j])[1]))

                current_date = str(
                    (self.monday_day + dt.timedelta(days=i)).date())
                lsn = self.lssn_lst_from_sql[j]

                if_row_exists = cur.execute(
                    f"SELECT * FROM all_stats WHERE date = '{current_date}' AND lesson = '{lsn}'").fetchall()

                if not if_row_exists:
                    cur.execute(
                        f"INSERT INTO all_stats VALUES('{current_date}', '{lsn}', '', '')")
        con.commit()
        con.close()

    def update_labels(self):
        self.month_lbl.setText(
            str(self.month_monday[0]) + ', ' + str(self.monday_day.year))

        self.monday_lbl.setText('Пн' + '\n' + str(self.monday_day.day))
        self.tuesday_lbl.setText('Вт' + '\n' +
                                 str((self.monday_day + dt.timedelta(days=1)).day))
        self.wednesday_lbl.setText('Ср' + '\n' +
                                   str((self.monday_day + dt.timedelta(days=2)).day))
        self.thursday_lbl.setText('Чт' + '\n' +
                                  str((self.monday_day + dt.timedelta(days=3)).day))
        self.friday_lbl.setText('Пт' + '\n' +
                                str((self.monday_day + dt.timedelta(days=4)).day))
        self.saturday_lbl.setText('Сб' + '\n' +
                                  str((self.monday_day + dt.timedelta(days=5)).day))

    def get_monday_info(self):

        # Формат: >>> 1
        self.date_monday = self.monday_day.day

        # Формат: >>> ('Понедельник', 0, 'Monday')
        self.week_day_monday = (WEEK_DAYS[self.monday_day.strftime(
            '%A')][0], WEEK_DAYS[self.monday_day.strftime('%A')][1],
            self.monday_day.strftime('%A'))

        # Формат: >>> ('Январь', 0)
        self.month_monday = (
            MONTHS[str(self.monday_day.month - 1)], self.monday_day.month - 1)

    def get_lessons_lst(self, week_day):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()
        self.lssn_lst_from_sql = cur.execute(
            EXECUTE_LESSONS, (week_day, )).fetchall()[0][1:]
        self.lsns_count = 9 - self.lssn_lst_from_sql.count(None)
        con.commit()
        con.close()

    def get_stats(self, week_day, crnt_lsn):
        current_date = (self.monday_day + dt.timedelta(days=week_day)).date()

        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()
        stats = cur.execute(
            "SELECT lesson, home_task, grade FROM all_stats WHERE date == ?", (current_date, )).fetchall()
        con.commit()
        con.close()

        task = None
        grade = None

        for stat in stats:
            if stat[0] == crnt_lsn:
                task = stat[1]
                grade = stat[2]

        return (task, grade)

    def save_diary(self):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()
        for i, table in enumerate(self.all_tables):
            current_date = str((self.monday_day + dt.timedelta(days=i)).date())
            for j in range(table.rowCount()):
                stat = []
                stat.append(current_date)
                stat.append(table.item(j, 0).text())
                stat.append(table.item(j, 1).text())
                stat.append(table.item(j, 2).text())
                try: 
                    if stat[3] == '':
                        cur.execute('UPDATE all_stats SET home_task = ? , grade = ? WHERE date = ? AND lesson = ?',
                                    (f"{stat[2]}", f"{stat[3]}", f"{stat[0]}", f"{stat[1]}"))
                    else:
                        cur.execute('UPDATE all_stats SET home_task = ? , grade = ? WHERE date = ? AND lesson = ?',
                                    (f"{stat[2]}", f"{int(stat[3])}", f"{stat[0]}", f"{stat[1]}"))

                except:
                    pass
        con.commit()
        con.close()
