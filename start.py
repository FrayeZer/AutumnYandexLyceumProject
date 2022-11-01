import sys

from main_window import MainWindow
from schedule import *
from diary import *

def main():
    app = QApplication(sys.argv)
    wnd = MainWindow()
    wnd.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
else:
    print(f'This .py file is not a module!')