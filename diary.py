from PyQt5.QtWidgets import *
from diary_ui import Ui_Diary

class Diary(QMainWindow, Ui_Diary):
    def __init__(self) -> None:
        super(Diary, self).__init__()
        self.setupUi(self)
        
        self.initobjs()

    def initobjs(self):
        pass



