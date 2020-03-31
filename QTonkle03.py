#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

# !/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton
from PySide2.QtGui import QIcon
import sys


class Pick(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.resize(30, 10)
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

    def setpos(self, x, y):
        offset = 25
        self.move(offset + 30 * x, 50 + 10 * y)


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

        self.setWindowTitle("QTInkle01")
        self.setGeometry(300, 300, 1200, 600)
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)
        self.setMaximumHeight(600)
        self.setMaximumWidth((1200))
        self.setIcon()  # todo sort out whether is works on Mac
        self.create_band(30, 20)

    def setIcon(self):
        appIcon = QIcon("/home/brian/.local/share/icons/hicolor/16x16/apps/97C1_wordpad.0.png")
        self.setWindowIcon(appIcon)

    def create_band(self, x, y):
        self.band = Band(self, "red", "yellow", x, y)
        for y in range(self.band.warp_ct):
            for x in range(self.band.pick_ct):
                self.band.warps[y].picks[x].clicked.connect(
                    lambda checked=self.band.warps[y].picks[x].isChecked(), i=x, j=y: self.alternate_pick(i, j))

    def alternate_pick(self, i, j):
        pick = self.band.warps[j].picks[i]
        hcol = self.band.warps[j].heddled_colour
        ucol = self.band.warps[j].unheddled_colour
        pickcol = ucol if pick.colour == hcol else hcol
        pick.setcolour(pickcol)


myApp = QApplication(sys.argv)
window = Window()
window.show()

myApp.exec_()
sys.exit(0)
