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
        self.colour=None

    def setColour(self, col):
        self.colour = col
        s = "background-color:" + col + ";"
        self.setStyleSheet(s)

    def getColour(self):
        return self.colour


class SingleWarp(Yarn):
    def __init__(self, parent, loom_pos):
        Yarn.__init__(self, parent)
        self.loom_position = loom_pos
        self.isHeddled = not bool(loom_pos % 2)


class Loom():
    def __init__(self, loom, band, warp_ct):
        self.warps = []
        self.band = []
        self.warp_ct = 0
        self.max_warps = 96
        self.max_picks = 19
        for i in range(warp_ct):
            self.add_warp_thread(loom)
            self.add_band_thread(band)

    def add_warp_thread(self, parent):
        x_offset = 25
        y_offset = 80
        if self.warp_ct < self.max_warps:
            loom_pos = self.warp_ct
            new_warp_thread = SingleWarp(parent, loom_pos)
            new_warp_thread.resize(10, 30)
            y = y_offset if new_warp_thread.isHeddled else y_offset + 30
            new_warp_thread.move(x_offset + loom_pos * 10, y)
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
            for pick in self.band[-1]:
                pick.setParent(None)
                pick.deleteLater()
            del self.band[-1]

    def add_band_thread(self, parent):
        x_offset = 15
        y_offset = 50
        band_row = []
        if self.warp_ct < self.max_warps:
            for pick in range(self.max_picks):
                new_pick = SingleWarp(parent, self.warp_ct)
                new_pick.isHeddled = bool((self.warp_ct + pick) % 2)
                new_pick.resize(30, 10)
                x = x_offset if self.warps[self.warp_ct - 1].isHeddled else x_offset + 30
                y = y_offset if self.warps[self.warp_ct - 1].isHeddled else y_offset + 5
                new_pick.move(x + 60 * pick, y + 11 * ((self.warp_ct - 1) // 2))
                new_pick.show()
                band_row.append(new_pick)
            self.band.append(band_row)
        return band_row


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
        self.loom = Loom(self.loom_frame, self.band_frame, 6)
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
            old_col = yarn.getColour()
            col = QColorDialog.getColor().name()
            yarn.setColour(col)
            if old_col:
                self.change_warp_colour(old_col, col)
        self.curbutton.setColour(yarn.getColour())

    def change_warp_colour(self, old_col, new_col):
        for warp in self.loom.warps:
            if warp.getColour()== old_col:
                warp.setColour(new_col)
            for row in self.loom.band:
                for pick in row:
                    if pick.getColour() == old_col:
                        pick.setColour(new_col)



    def add_warp_thread(self):
        warp = self.loom.add_warp_thread(self.loom_frame)
        warp.clicked.connect(lambda: self.colour_warp_thread(warp.loom_position))
        band_warp = self.loom.add_band_thread(self.band_frame)
        for i, pick in enumerate(band_warp):
            pick.clicked.connect(lambda: self.colour_pick(warp.loom_position, i))

    def remove_warp_thread(self):
        self.loom.remove_warp_thread()

    def colour_warp_thread(self, warp):
        this_warp = self.loom.warps[warp]
        this_warp.setColour(self.curbutton.getColour())
        for pick in self.loom.band[warp]:
            pick.setColour(self.curbutton.getColour())


if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    sys.exit(0)
