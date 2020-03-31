#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'


from PySide2.QtWidgets import QApplication, QWidget,QPushButton
from PySide2.QtGui import QIcon
import sys


class MyButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.resize(30,10)
        self.setStyleSheet(""" MyButton {                      
                            border - style: outset;
                            border - width: 50 px;
                            border - radius: 2000px;
                            border - color: white;
                            padding: 4 px;
                            }""")

    def setinitcolour(self,x,y):
        if (x+y) % 2:
            s = "red"
        else:
            s = "yellow"
        self.setcolour(s)

    def setcolour(self,col):
        s="background-color:" + col+";"
        self.setStyleSheet(s)

    def setpos(self,x,y):
        # if y % 2:
        #     offset = 25
        # else:
        #
        offset = 25
        self.move(offset + 30 * x, 50 + 10 * y)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("QTInkle01")
        self.setGeometry(300,300,1200,600)
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        self.setMaximumHeight(600)
        self.setMaximumWidth((1200))
        self.setIcon() # todo sort out whether is works on Mac
        self.display_band()

    def setIcon(self):
        appIcon = QIcon("/home/brian/.local/share/icons/hicolor/16x16/apps/97C1_wordpad.0.png")
        self.setWindowIcon(appIcon)

    def _pick_row(self):
        self.picks = []
        for y in range(10):
            self.picks.append(MyButton(self))
        return self.picks

    def display_band(self):
        self.band = []
        for x in range(30):
            pick_row=self._pick_row()
            for y in range(len(pick_row)):
                pick_row[y].setpos(x,y)
                pick_row[y].setinitcolour(x, y)
                pick_row[y].clicked.connect(lambda checked=pick_row[y].isChecked(), i=x, j=y: self.btnclick(i,j))
            self.band.append(pick_row)

    def btnclick(self,i,j):
        self.band[i][j].setcolour("blue")


myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)