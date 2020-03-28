#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QIcon
import sys


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("QTInkle01")
        self.setGeometry(300,300,300,300)
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        self.setMaximumHeight(300)
        self.setMaximumWidth((400))
        self.setIcon() # todo sort out whether is works on Mac

    def setIcon(self):
        appIcon = QIcon("/home/brian/.local/share/icons/hicolor/16x16/apps/97C1_wordpad.0.png")
        self.setWindowIcon(appIcon)


myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)