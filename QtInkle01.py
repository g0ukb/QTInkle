#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget,QPushButton
from PySide2.QtGui import QIcon
import sys





class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("QTInkle01")
        self.setGeometry(300,300,600,600)
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        self.setMaximumHeight(600)
        self.setMaximumWidth((800))
        self.setIcon() # todo sort out whether is works on Mac
        self.BtnArray()


    def setIcon(self):
        appIcon = QIcon("/home/brian/.local/share/icons/hicolor/16x16/apps/97C1_wordpad.0.png")
        self.setWindowIcon(appIcon)


    # def BtnArray(self):
    #     self.btn = []
    #     for x in range(10):
    #         for y in range(5):
    #           self.btn.append(self.InkleBtn(x,y))

    def BtnArray(self):
        def setcol(col):
            s="background-color:" + col
            return self.setStyleSheet(s)

        self.btn = []
        for x in range(10):
           for y in range(5):
             self.btn.append(QPushButton(self))
             if y%2:
                 offset=25
             else:
                 offset=50
             self.btn[x*5+y].resize(60,20)
             self.btn[x*5+y].move(offset+50*x,50+20*y)
             if x%2:
                 s="red"
             else:
                 s="yellow"
             self.btn[x * 5 + y].setcol(s)


myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)