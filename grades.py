import sqlite3
import datetime as dt
import csv

from PyQt5.QtWidgets import *
from grades_ui import *


class Grades(QMainWindow, Ui_Grades):
    def __init__(self) -> None:
        super(Grades, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Оценки')

        self.initobjs()

    def initobjs(self):        
        self.fill_table()
        self.update_grades_btn.clicked.connect(self.update_grades)
        self.fill_table()
        self.fill_table()

    def fill_table(self):
        self.get_all_lslns_lst()

        self.grades_table.setColumnCount(2)
        self.grades_table.setRowCount(len(self.all_lslns_lst))

        # Заполняю предметы
        for i in range(self.grades_table.rowCount()):
            self.grades_table.setItem(
                i, 0, QTableWidgetItem(self.all_lslns_lst[i]))

            # Список всех оценок для текущего i-того предмета в таблице
            # \/ \/ \/ 
            grades = self.get_grades(lst_number=i)

            if len(grades) >= self.grades_table.columnCount():
                self.grades_table.setColumnCount(len(grades) + 2)

            # Заполняю оценки
            for j in range(len(grades)):
                self.grades_table.setItem(
                    i, j + 1, QTableWidgetItem(str(grades[j][0])))

        # Заполняю средний балл
        for i in range(self.grades_table.rowCount()):
            grades = self.get_grades(lst_number=i)

            sum_grades = sum([int(grade[0]) for grade in grades])
            if len(grades):
                average_grade = str(round(sum_grades / len(grades), 2))
            else:
                average_grade = ''
            self.grades_table.setItem(
                i, self.grades_table.columnCount() - 1, QTableWidgetItem(average_grade))

        self.grades_table.setHorizontalHeaderLabels(
            ['Предмет', *[str(i + 1) for i in range(self.grades_table.columnCount() - 2)], 'Средний балл'])

        # Очищаю от текста csv файл
        with open('grades.csv', 'wt', encoding='utf8') as removetext:
            writer = csv.writer(
                    removetext, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)    
            writer.writerow([])

        # Записываю все оценки в csv файл
        with open('grades.csv', 'at', encoding='utf8', newline='') as csvf: 
            writer = csv.writer(
                    csvf, delimiter=';', quotechar='"',
                    quoting=csv.QUOTE_MINIMAL)
            line = []
            writer.writerow(['Предмет', *[str(i + 1) + 'оценка' for i in range(self.grades_table.columnCount() - 2)], 'Средний балл'])
            for i in range(self.grades_table.rowCount()):
                for j in range(self.grades_table.columnCount()):
                    try:
                        line.append(self.grades_table.item(i, j).text())
                    except:
                        line.append('_')
                writer.writerow(line)
                line = []



    def get_all_lslns_lst(self):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()

        # Получаю список всех предметов из расписания, убираю дубликаты с помощью множеств
        self.all_lslns_set = set()
        self.lslns_lst = cur.execute('SELECT * FROM Schedule').fetchall()
        for lsns in self.lslns_lst:
            for lsn in lsns[1:]:
                self.all_lslns_set.add(lsn)
        self.all_lslns_set.remove(None)

        self.all_lslns_lst = sorted(list(self.all_lslns_set))
        con.commit()
        con.close()

    def get_grades(self, lst_number):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()

        # Список всех оценок по конкретному предмету
        self.grades = cur.execute("SELECT grade FROM all_stats WHERE lesson = ? and grade != ''", (
            self.all_lslns_lst[lst_number], )).fetchall()
        con.commit()
        con.close()
        return self.grades

    def update_grades(self):
        self.fill_table()
