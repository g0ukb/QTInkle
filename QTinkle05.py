#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox


from PySide2.QtGui import QFont, qApp
from PySide2.QtCore import *
import sys

import sys

class SinglePick(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(""" MyButton {                      
                            border - style: outset;
                            border - width: 50 px;
                            border - radius: 2000px;
                            border - color: white;
                            padding: 4 px;
                            }""")
        self.resize(30, 10)

    def setcolour(self, col):
        self.colour = col
        s = "background-color:" + col + ";"
        self.setStyleSheet(s)

    def setpos(self, x, y):
        offset = 40
        self.move(offset + 31 * x, 50 + 11 * y)


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


class SingleLoomWarp(Yarn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(10,30)


class CompleteLoomWarp():
    def __init__(self,parent, bout_ct):
        xoffset=20
        yoffset=80
        self.warp=[]
        for i in range(bout_ct):
            newwarp = SingleLoomWarp(parent)
            y = yoffset+30 if i%2 else yoffset
            newwarp.move(xoffset + i * 10, y)
            if i>=10:
                pass
                newwarp.hide()
            self.warp.append(newwarp)



class SingleBandWarp():
    def __init__(self, parent, start_heddled, heddled_colour, unheddled_colour, pick_ct, warp_row=0):
        self.start_heddled = start_heddled
        self.heddled_colour = heddled_colour
        self.unheddled_colour = unheddled_colour
        self.warp_row = warp_row
        self.picks = []
        for x in range(pick_ct):
            newpick = SinglePick(parent)
            newpick.setpos(x, self.warp_row)
            if not (x % 2 == self.start_heddled):
                col = self.heddled_colour
            else:
                col = self.unheddled_colour
            newpick.setcolour(col)
            self.picks.append(newpick)


class CompleteBand():
    def __init__(self, parent, heddled_colour, unheddled_colour, pick_ct, warp_ct):
        self.warp_ct = warp_ct
        self.pick_ct = pick_ct
        self.warps = []
        for y in range(warp_ct):
            start_heddled = y % 2
            self.warps.append(SingleBandWarp(parent, start_heddled, heddled_colour, unheddled_colour, pick_ct, y))


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("Inkle Designer")
        self.setFixedSize(1200,700)
        #self.setGeometry(300, 300, 1200, 700)
        # self.setMinimumHeight(100)
        # self.setMinimumWidth(250)
        # self.setMaximumHeight(700)
        # self.setMaximumWidth((1200))
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSize(16)
        self.yarnframe()
        self.loomframe()
        self.threadct=0
        self.unheddlednext=False
        self.weaveframe()
        self.create_band(36, 20)


    def yarnframe(self):
        yarn_frame = QFrame(self)
        yarn_frame.setFrameShape(QFrame.StyledPanel)
        yarn_frame.setGeometry(0, 0, 200, 200)
        yarnbox = QVBoxLayout()
        title=QLabel("Yarns")
        title.setFont(self.titleFont)
        title.setAlignment(Qt.AlignCenter)
        yarnbox.addWidget(title)
        btngrid = QGridLayout()
        btngrid.setColumnStretch(1, 4)
        btngrid.setColumnStretch(2, 4)
        btngrid.setColumnStretch(3, 4)
        self.create_yarns()
        for i in range(12):
            btngrid.addWidget(self.yarns[i])
        yarnbox.addLayout(btngrid)
        lockbox=QHBoxLayout()
        self.yarnlock=QCheckBox("Lock Colours")
        lockbox.addWidget(self.yarnlock)
        yarnbox.addLayout(lockbox)
        curbox = QHBoxLayout()
        curbox.addWidget(QLabel("Current"))
        self.curbutton = Yarn()
        curbox.addWidget(self.curbutton)
        curbox.insertSpacing(40,40)
        yarnbox.addLayout(curbox)
        yarn_frame.setLayout(yarnbox)


    def loomframe(self):
        self.loom_frame = QFrame(self)
        self.loom_frame.setFrameShape(QFrame.StyledPanel)
        self.loom_frame.setGeometry(200, 0, 1000, 200)
        title=QLabel(self.loom_frame)
        title.setText("Loom")
        title.setGeometry(400,14,200,20)
        title.setFont(self.titleFont)
        self.boutplus=QPushButton(self.loom_frame)
        self.boutplus.setText("Thread +")
        self.boutplus.move(10,40)
        self.boutplus.clicked.connect(lambda: self.addthread())
        self.boutminus = QPushButton(self.loom_frame)
        self.boutminus.setText("Thread -")
        self.boutminus.move(910, 40)
        self.heddled=CompleteLoomWarp(self.loom_frame, 96)


    def weaveframe(self):
        self.weave_frame = QFrame(self)
        self.weave_frame.setFrameShape(QFrame.StyledPanel)
        self.weave_frame.setGeometry(0, 200, 1200, 500)
        title=QLabel(self.weave_frame)
        title.setText("Band")
        title.setGeometry(600,14,200,20)
        title.setFont(self.titleFont)

    def create_band(self, x, y):
        self.band = CompleteBand(self.weave_frame, "red", "yellow", x, y)
        for y in range(self.band.warp_ct):
            for x in range(self.band.pick_ct):
                self.band.warps[y].picks[x].clicked.connect(
                    lambda checked=self.band.warps[y].picks[x].isChecked(), i=x, j=y: self.swap_pick_colour(i, j))

    def swap_pick_colour(self, i, j):
        pick = self.band.warps[j].picks[i]
        hcol = self.band.warps[j].heddled_colour
        ucol = self.band.warps[j].unheddled_colour
        pickcol = ucol if pick.colour == hcol else hcol
        pick.setcolour(pickcol)

    def create_yarns(self):
        self.yarns = []
        for i in range(12):
            btn = Yarn()
            self.yarns.append(btn)
            self.yarns[i].clicked.connect(
                lambda checked=self.yarns[i].isChecked(), x=i: self.yarn_colour(x))

    def yarn_colour(self, i):
        yarn=self.yarns[i]
        if not self.yarnlock.isChecked():
            col = QColorDialog.getColor().name()
            yarn.setcolour(col)
        col= yarn.palette().button().color().name()
        self.curbutton.setcolour(col)

    def addthread(self):
        if self.unheddlednext:
            self.unheddled.warp[self.threadct].show()
            self.threadct += 1

        else:
            self.heddled.warp[self.threadct].show()
        self.unheddlednext = not self.unheddlednext


myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)
