import sqlite3
import datetime as dt

from PyQt5.QtWidgets import *
from schedule_ui import Ui_Schedule

WEEK_DAYS = {
    'Monday': ['Понедельник', 0],
    'Tuesday': ['Вторник', 1],
    'Wednesday': ['Среда', 2],
    'Thursday': ['Четверг', 3],
    'Friday': ['Пятница', 4],
    'Saturday': ['Суббота', 5],
    'Sunday': ['Воскресенье', 0]
}

# Пришлось создать второй аналогичный словарь. Я бы мог исправить это, но..
# Мне лень..
WEEK_DAYS_INDEXES = {
    '0': 'Понедельник',
    '1': 'Вторник',
    '2': 'Среда',
    '3': 'Четверг',
    '4': 'Пятница',
    '5': 'Суббота',
    '6': 'Воскресенье',
}

EXECUTE_LESSONS = '''
    SELECT * FROM Schedule
    WHERE day == ?
'''

EXECUTE_BELLS_SCHEDULE = '''
    SELECT lesson_starts FROM bells_schedule
    WHERE lesson_number == ?
'''


class Schedule(QMainWindow, Ui_Schedule):
    def __init__(self) -> None:
        super(Schedule, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Расписание')

        self.initobjs()

    def initobjs(self):

        # В расписании выбираю текущий день недели. Если сегодня
        # воскресенье, то выбираю понедельник.
        self.days_of_week.setCurrentIndex(
            WEEK_DAYS[dt.datetime.now().strftime('%A')][1])

        self.lessons_table.setColumnCount(3)
        self.lessons_table.setHorizontalHeaderLabels(
            ['Предмет', 'Время', 'Перемена'])
        self.days_of_week.currentIndexChanged.connect(self.fill_table)
        self.fill_table()

        self.add_lsn.clicked.connect(self.add_lesson)
        self.remove_lsn.clicked.connect(self.remove_lesson)
        self.upd_btn.clicked.connect(self.update_table)
        self.save_btn.clicked.connect(self.show_dialog)

    def fill_table(self):

        # Получаю все необходимые данные для заполнения таблицы
        self.get_lessons_lst()
        self.get_bells_schedule()
        self.calc_breaks()

        # Если в таблице sqlite есть пустые ячейки, я их не добавляю, т.е.
        # избавляюсь от пустых строк в QTable. Далее запонляю таблицу.
        self.lessons_table.setRowCount(self.lsns_count)

        for i, lssn in enumerate(self.lssn_lst_from_sql):
            if lssn != None:
                self.lessons_table.setItem(i, 0, QTableWidgetItem(lssn))
                self.lessons_table.setItem(
                    i, 1, QTableWidgetItem(str(self.bells_schedule[i])))
                self.lessons_table.setItem(i, 2, QTableWidgetItem(
                    str(self.break_schedule[i]) + ' мин'))

    def add_lesson(self):
        self.lessons_table.setRowCount(self.lessons_table.rowCount() + 1)

    def remove_lesson(self):
        self.lessons_table.setRowCount(self.lessons_table.rowCount() - 1)

    def get_lessons_lst(self):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()
        self.lssn_lst_from_sql = cur.execute(
            EXECUTE_LESSONS, (self.days_of_week.currentText(), )).fetchall()[0][1:]
        self.lsns_count = 9 - self.lssn_lst_from_sql.count(None)
        con.commit()
        con.close()

    def get_bells_schedule(self):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()
        self.bells_schedule = []
        for j in range(self.lsns_count):
            self.bells_schedule.append(cur.execute(
                EXECUTE_BELLS_SCHEDULE, (j + 1, )).fetchall()[0][0])
        con.commit()
        con.close()

    def update_table(self):
        self.fill_table()

    def calc_breaks(self):
        self.break_schedule = []
        for i in range(len(self.bells_schedule)):
            start_time_as_dt_obj = dt.datetime(
                1, 1, 1, *map(int, self.bells_schedule[i].split(':')))
            start_time_plus_45min = start_time_as_dt_obj + \
                dt.timedelta(minutes=45)
            try:

                # Пытаюсь получить время начала i-того + 1 урока до тех пор,
                # пока не выйду за рамки длины списка уроков (из-за i + 1 вместо i).
                next_start_time = dt.datetime(
                    1, 1, 1, *map(int, self.bells_schedule[i + 1].split(':')))
            except:

                # Если вышел за рамки списка (спойлер: это гарантированный случай),
                # то ничего не делаю, ибо так сделать быстрее всего.
                pass

            # Если уроки пересекаются, вывожу соответствующую ошибку
            try:
                break_duration = next_start_time - \
                    dt.timedelta(hours=start_time_plus_45min.hour,
                                 minutes=start_time_plus_45min.minute)
                self.break_schedule.append(break_duration.strftime('%M'))
            except:
                if i + 1 != len(self.bells_schedule):
                    break_duration = 'Вам явно стоит подучить математику, ведь урок начинается в ' \
                        'момент, когда предыдущий еще не закончился! Перемена 0'
                else:

                    # Если это последний урок, то вместо ошибки добавляю 0,
                    # т.к. в этом случае ошибка появляется как раз из-за того,
                    # что это последний в списке урок, после него список заканчивается
                    break_duration = 0
                self.break_schedule.append(break_duration)

    def save_table(self):
        con = sqlite3.connect('diary.sqlite')
        cur = con.cursor()
        exec_schedule = '''UPDATE Schedule SET '''
        sql_elems_for_save = []

        for i in range(1, self.lessons_table.rowCount() + 1):

            # Сохраняю расписание
            if self.lessons_table.item(i - 1, 0) != None:
                sql_elems_for_save.append(
                    f"'{str(i)}' = '{self.lessons_table.item(i - 1, 0).text()}'")
            else:
                sql_elems_for_save.append(f"'{str(i)}' = '(Урок)'")

            # Пытаюсь сохранить время начала урока
            try:
                dt.datetime(
                    1, 1, 1, *map(int, self.lessons_table.item(i - 1, 1).text().split(':')))
                cur.execute("UPDATE bells_schedule SET lesson_starts = ? WHERE lesson_number == ?",
                            (f"{self.lessons_table.item(i - 1, 1).text()}", i))
            except:
                pass

        # Заменяю значения с названиями уроков, которые находятся в
        # ячейках, выходящих за рамки QTable.rowCount() на NULL для корректного отображения
        if self.lessons_table.rowCount() < self.lsns_count:
            for i in range(self.lessons_table.rowCount() + 1, self.lsns_count + 1):
                sql_elems_for_save.append(f"'{str(i)}' = NULL")

        # Если ячеек в БД нехватает для сохранения таблицы QTable, вывожу сообщение ...
        try:
            cur.execute(exec_schedule + ', '.join(sql_elems_for_save) +
                        f" WHERE day == '{self.days_of_week.currentText()}'")
        except sqlite3.OperationalError:
            print('\n\n\n-------------------------- \n Вы что, садист? 10 уроков???..'
                  'неет, я этого вам не позволю. \n--------------------------')

        con.commit()
        con.close()

    def show_dialog(self):
        dlg = CustomDialog()
        if dlg.exec():
            self.save_table()


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(" ")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Close

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel('Подтвердить изменения?')
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
