#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog,QLabel, QHBoxLayout


from PySide2.QtGui import QIcon
from PySide2.QtCore import QRect
import sys

class Pick(QPushButton):
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

class BandRow():
    def __init__(self, parent, start_heddled, heddled_colour, unheddled_colour, pick_ct, warp_row=0):
        self.start_heddled = start_heddled
        self.heddled_colour = heddled_colour
        self.unheddled_colour = unheddled_colour
        self.warp_row = warp_row
        self.picks = []
        for x in range(pick_ct):
            newpick = Pick(parent)
            newpick.setpos(x, self.warp_row)
            if not (x % 2 == self.start_heddled):
                col = self.heddled_colour
            else:
                col = self.unheddled_colour
            newpick.setcolour(col)
            self.picks.append(newpick)


class Band():
    def __init__(self, parent, heddled_colour, unheddled_colour, pick_ct, warp_ct):
        self.warp_ct = warp_ct
        self.pick_ct = pick_ct
        self.warps = []
        for y in range(warp_ct):
            start_heddled = y % 2
            self.warps.append(BandRow(parent, start_heddled, heddled_colour, unheddled_colour, pick_ct, y))

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("QTInkle04")
        self.setGeometry(300, 300, 1200, 700)
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        self.setMaximumHeight(700)
        self.setMaximumWidth((1200))
        self.setframes()
        self.create_band(36, 20)





    def setframes(self):
        #self.yarn_frame = QGroupBox("Grid")
        self.yarn_frame =QFrame(self)
        self.yarn_frame.setFrameShape(QFrame.StyledPanel)
        self.yarn_frame.setGeometry(0, 0, 200, 200)
        self.createGridLayout()
        self.yarn_frame.setLayout(self.titlelayout)
              #frame.setLineWidth(0.6)
        self.loom_frame =QFrame(self)
        self.loom_frame.setFrameShape(QFrame.StyledPanel)
        self.loom_frame.setGeometry(200, 0, 1000, 200)
        self.weave_frame =QFrame(self)
        self.weave_frame.setFrameShape(QFrame.StyledPanel)
        self.weave_frame.setGeometry(0, 200, 1200, 500)

    def createGridLayout(self):
        #self.horizontalGroupBox = QGroupBox("Grid")
        self.titlelayout=QHBoxLayout()
        self.titlelayout.addWidget(QLabel("Yarns123456"))

        self.layout = QGridLayout()
        self.titlelayout.addWidget(self.layout)
        self.layout.addWidget(QLabel("Yarns123456"))
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)
        self.layout.setColumnStretch(3, 4)
        self.create_yarns()
        for i in range(12):
            self.layout.addWidget(self.yarns[i])
            self.yarns[i].clicked.connect(
                lambda checked=self.yarns[i].isChecked(), x=i: self.yarn_colour(x))
        self.layout.addWidget(QLabel("Current"))
        #self.yarn_frame.setLayout(self.layout)

    def create_band(self, x, y):
        self.band = Band(self.weave_frame, "red", "yellow", x, y)
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
        self.yarns=[]
        for i in range(12):
            btn=QPushButton()
            self.yarns.append(btn)


    def yarn_colour(self,i):
        col=QColorDialog.getColor()
        s = "background-color:" + col.name()
        self.yarns[i].setStyleSheet(s)







myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)