#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox

from PySide2.QtGui import QFont, qApp
from PySide2.QtCore import *
import sys


class Yarn(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(""" MyButton {                      
                            border - style: outset;
                            border - width: 50 px;
                            border - radius: 2000px;
                            border - color: white;
                            padding: 4 px;
                            }""")


    def setcolour(self, col):
        self.colour = col
        s = "background-color:" + col + ";"
        self.setStyleSheet(s)

    def getcolour(self):
        return self.palette().button().color().name()


class SingleWarp(Yarn):
    def __init__(self, parent, loom_pos):
        Yarn.__init__(self, parent)
        self.loom_position = loom_pos
        self.heddled = not bool(loom_pos % 2)


class Loom():
    def __init__(self, parent, warp_ct):
        self.x_offset = 20
        self.y_offset = 80
        self.warps = []
        self.warp_ct = 0
        for i in range(warp_ct):
            self.add_warp_thread(parent)

    def add_warp_thread(self, parent):
        if self.warp_ct < 96:
            loom_pos = self.warp_ct
            new_warp_thread = SingleWarp(parent, loom_pos)
            new_warp_thread.resize(10, 30)
            y = self.y_offset if new_warp_thread.heddled else self.y_offset + 30
            new_warp_thread.move(self.x_offset + loom_pos * 10, y)
            new_warp_thread.show()
            self.warps.append(new_warp_thread)
            self.warp_ct += 1
            return new_warp_thread

    def remove_warp_thread(self):
        if self.warp_ct > 0:
            self.warp_ct -= 1
            self.warps[-1].setParent(None)
            self.warps[-1].deleteLater()
            del self.warps[-1]

class BandRow():
    def __init__(self, parent, start_heddled, heddled_colour, unheddled_colour, pick_ct, warp_row=0):
        self.start_heddled = start_heddled
        self.heddled_colour = heddled_colour
        self.unheddled_colour = unheddled_colour
        self.warp_row = warp_row
        self.picks = []
        for x in range(pick_ct):
            newpick = Yarn(parent)
            newpick.setpos(x, self.warp_row)
            if not (x % 2 == self.start_heddled):
                col = self.heddled_colour
            else:
                col = self.unheddled_colour
            newpick.setcolour(col)
            self.picks.append(newpick)


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Inkle Designer")
        self.setFixedSize(1200, 700)
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSize(16)
        self.create_yarn_frame()
        self.create_loom_frame()
        self.create_band_frame()
        self.loom = Loom(self.loom_frame, 2)
        for warp in self.loom.warps:
            warp.clicked.connect(lambda checked=warp.isChecked(), i=warp.loom_position: self.colour_warp_thread(i))

    def create_yarn_frame(self):
        yarn_frame = QFrame(self)
        yarn_frame.setFrameShape(QFrame.StyledPanel)
        yarn_frame.setGeometry(0, 0, 200, 200)
        yarnbox = QVBoxLayout()
        title = QLabel("Yarns")
        title.setFont(self.titleFont)
        title.setAlignment(Qt.AlignCenter)
        yarnbox.addWidget(title)
        yarngrid = QGridLayout()
        yarngrid.setColumnStretch(1, 4)
        yarngrid.setColumnStretch(2, 4)
        yarngrid.setColumnStretch(3, 4)
        self.create_yarns()
        for i in range(12):
            yarngrid.addWidget(self.yarns[i])
        yarnbox.addLayout(yarngrid)
        lockbox = QHBoxLayout()
        self.yarnlock = QCheckBox("Lock Colours")
        lockbox.addWidget(self.yarnlock)
        yarnbox.addLayout(lockbox)
        curbox = QHBoxLayout()
        curbox.addWidget(QLabel("Current"))
        self.curbutton = Yarn()
        curbox.addWidget(self.curbutton)
        curbox.insertSpacing(40, 40)
        yarnbox.addLayout(curbox)
        yarn_frame.setLayout(yarnbox)

    def create_loom_frame(self):
        self.loom_frame = QFrame(self)
        self.loom_frame.setFrameShape(QFrame.StyledPanel)
        self.loom_frame.setGeometry(200, 0, 1000, 200)
        title = QLabel(self.loom_frame)
        title.setText("Loom")
        title.setGeometry(400, 14, 200, 20)
        title.setFont(self.titleFont)
        self.add_warp_btn = QPushButton(self.loom_frame)
        self.add_warp_btn.setText("Thread +")
        self.add_warp_btn.move(10, 40)
        self.add_warp_btn.clicked.connect(lambda: self.add_warp_thread())
        self.remove_warp_btn = QPushButton(self.loom_frame)
        self.remove_warp_btn.setText("Thread -")
        self.remove_warp_btn.move(910, 40)
        self.remove_warp_btn.clicked.connect(lambda: self.remove_warp_thread())


    def create_band_frame(self):
        self.band_frame = QFrame(self)
        self.band_frame.setFrameShape(QFrame.StyledPanel)
        self.band_frame.setGeometry(0, 200, 1200, 500)
        title = QLabel(self.band_frame)
        title.setText("Band")
        title.setGeometry(600, 14, 200, 20)
        title.setFont(self.titleFont)


    def create_yarns(self):
        self.yarns = []
        for i in range(12):
            yarn = Yarn()
            self.yarns.append(yarn)
            self.yarns[i].clicked.connect(
                lambda checked=self.yarns[i].isChecked(), x=i: self.yarn_colour(x))

    def yarn_colour(self, i):
        yarn = self.yarns[i]
        if not self.yarnlock.isChecked():
            col = QColorDialog.getColor().name()
            yarn.setcolour(col)
        self.curbutton.setcolour(yarn.getcolour())

    def add_warp_thread(self):
        warp=self.loom.add_warp_thread(self.loom_frame)
        warp.clicked.connect(lambda: self.colour_warp_thread(warp.loom_position))

    def remove_warp_thread(self):
        self.loom.remove_warp_thread()

    def colour_warp_thread(self, warp):
        self.loom.warps[warp].setColour(self.curbutton.getcolour())


if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    sys.exit(0)
