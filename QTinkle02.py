#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'


from PySide2.QtWidgets import QApplication, QWidget,QPushButton
from PySide2.QtGui import QIcon
import sys


class MyButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(60,20)


    def setinitcolour(self,x,y):
        if (x+y) % 2:
            s = "red"
        else:
            s = "yellow"
        self.setcolour(s)

    def setcolour(self,col):
        self.setStyleSheet("background-color:" + col)

    def setpos(self,x,y):
        # if y % 2:
        #     offset = 25
        # else:
        #
        offset = 25
        self.move(offset + 50 * x, 50 + 20 * y)

# class BtnArray():
#     def __init__(self):
#         self.btns=[]
#         self.addBtn()
#
#     def addBtn(self):
#         btn=MyButton(self)
#         btn.setpos(x,y)
#         btn.setinitcolour(x)
#         idx=x*5+y
#         self.btns.append(btn)






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
        #self.bnta=BtnArray()


    def setIcon(self):
        appIcon = QIcon("/home/brian/.local/share/icons/hicolor/16x16/apps/97C1_wordpad.0.png")
        self.setWindowIcon(appIcon)


    def BtnArray(self):
        self.btn = []
        for x in range(10):
           for y in range(5):
             idx=x*5+y

             self.btn.append(MyButton(self))
             #self.btn[idx].
             self.btn[idx].setpos(x,y)
             self.btn[idx].setinitcolour(x,y)
             self.btn[idx].clicked.connect(lambda checked=self.btn[idx].isChecked(), i=idx : self.btnclick( i) )

    def btnclick(self,i):
        print(i)
        self.btn[i].setcolour("blue")


myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)