#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox, QMainWindow, QAction, QFileDialog, QMessageBox, QSpinBox

from PySide2.QtGui import QFont, QPixmap
from PySide2.QtCore import *
# from guppy import hpy

class C1(QColorDialog):
    def __init__(self,parent=None):
        super(C1, self).__init__(parent)


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(250, 250, 800, 800);

        d = C1(self)
        self.setCentralWidget(d)
        d.setWindowFlags(Qt.SubWindow)
        #d.setWindowFlags(QWidget)
        d.setOptions(QColorDialog.DontUseNativeDialog)
        d.setOptions(QColorDialog.NoButtons)
        b=QPushButton(d)
        b.move(200,200)





myApp = QApplication()
window = Window()
window.show()
myApp.exec_()
