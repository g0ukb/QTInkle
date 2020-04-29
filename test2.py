#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox, QMainWindow, QAction, QFileDialog, QMessageBox, QDialog

from PySide2.QtGui import QFont, QPixmap, QColor
from PySide2.QtCore import *


# from guppy import hpy

class C1(QColorDialog):
    def __init__(self, parent=None):
        super(C1, self).__init__(parent)
        self.setGeometry(0, 0, 500, 420);

class C2(QDialog):
    def __init__(self, parent=None):
        super(C2, self).__init__(parent)
        self.setGeometry(250, 250, 600, 450);
        self.setWindowTitle("Yarn Picker")
        self.d=C1(self)
        self.d.move(0,0)

        #self.col=d.getColor()
        self.d.setWindowFlags(Qt.SubWindow)
        self.d.setOptions(QColorDialog.DontUseNativeDialog)
        self.d.setOptions(QColorDialog.NoButtons)

        b = QPushButton(self)
        b.move(100, 400)
        b.setText("Hello")
        b.clicked.connect(self.leave)

        bb = QPushButton(self)
        bb.move(200, 400)
        bb.setText("Goodbye")
        bb.clicked.connect(self.cancel)


    def leave(self):
        print("Here")
        self.accept()

    def cancel(self):
        print("There")
        self.reject()


    def getinfo(self):
        result=self.exec_()
        col = self.d.currentColor()
        c=col.name()
        return c,"Hello",result==QDialog.Accepted

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(250, 250, 800, 800);
        d = C2(self)
        self.setCentralWidget(d)
        # if d.exec_():
        #     a=d.getinfo()
        col,text,result =d.getinfo()
        if result:
            print(col,text)
        else:
            print("Cancelled")

        # d.setWindowFlags(QWidget)


myApp = QApplication()
window = Window()
window.show()
myApp.exec_()

