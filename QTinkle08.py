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
        self.colour = None
        self.colour_index=None

    def setColour(self, col):
        self.colour = col
        try:
            s = "background-color:" + col + ";"
            self.setStyleSheet(s)
        except TypeError:
            pass

    def getColour(self):
        return self.colour


class SingleWarp(Yarn):
    def __init__(self, parent, warp_no):
        Yarn.__init__(self, parent)
        self.warp_number = warp_no
        self.isHeddled = not bool(warp_no % 2)


class SinglePick(SingleWarp):
    def __init__(self, parent, warp_no):
        SingleWarp.__init__(self, parent, warp_no)
        self.alt_colour = None
        self.isPicked = False
        self.pick_number=0

    def setAltColour(self, col):
        self.alt_colour = col

    def getAltColour(self):
        return self.alt_colour

    def doPickup(self):
        self.colour, self.alt_colour = self.alt_colour, self.colour
        self.setColour(self.colour)
        self.setAltColour(self.alt_colour)
        self.isPicked = not self.isPicked


class Loom():
    def __init__(self, loom, band, warp_ct):
        self.warps = []
        self.band = []
        self.warp_ct = 0
        self.max_warps = 80
        self.max_picks = 20
        for i in range(warp_ct):
            self.add_new_warp(loom, band)

    def add_new_warp(self, loom, band):
        warp_no = self.warp_ct
        if warp_no < self.max_warps:
            loom_warp = self.add_warp_thread(loom, warp_no)
            band_warp = self.add_band_thread(band, warp_no)
            self.warp_ct += 1
            return loom_warp, band_warp
        else:
            return None, None

    def add_warp_thread(self, parent, warp_no):
        x_offset = 100
        y_offset = 80
        new_warp_thread = SingleWarp(parent, warp_no)
        new_warp_thread.resize(10, 30)
        y = y_offset if new_warp_thread.isHeddled else y_offset + 30
        new_warp_thread.move(x_offset + warp_no * 10, y)
        new_warp_thread.show()
        self.warps.append(new_warp_thread)
        return new_warp_thread

    def add_band_thread(self, parent, warp_no):
        x_offset = 20
        y_offset = 50
        band_row = []
        pick_no=0
        for pick in range(self.max_picks):
            new_pick = SinglePick(parent, warp_no)
            new_pick.pick_number=pick_no
            new_pick.isHeddled = not bool(warp_no % 2)
            new_pick.resize(29, 11)
            x = x_offset if new_pick.isHeddled else x_offset + 29
            y = y_offset if new_pick.isHeddled else y_offset + 5
            new_pick.move(x + 58 * pick, y + 11 * (warp_no // 2))
            new_pick.show()
            band_row.append(new_pick)
            pick_no+=1
        self.band.append(band_row)
        return band_row

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
            warp.clicked.connect(lambda checked=warp.isChecked(), i=warp.warp_number: self.colour_warp_thread(i))
        for band_row in self.loom.band:
            for pick in band_row:
                pick.clicked.connect(
                    lambda checked=pick.isChecked(), i=pick.warp_number, j=pick.pick_number: self.pickup(i, j))

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
            self.yarns[i].colour_index=i
        yarnbox.addLayout(yarngrid)
        lockbox = QHBoxLayout()
        self.yarnlock = QCheckBox("Lock Colours")
        lockbox.addWidget(self.yarnlock)
        yarnbox.addLayout(lockbox)
        curbox = QHBoxLayout()
        curbox.addWidget(QLabel("Current"))
        self.current_yarn_colour = Yarn()
        self.current_yarn_colour.clicked.connect(lambda: self.get_next_colour())
        self.current_yarn_colour.clicked.connect(lambda: self.debug())
        curbox.addWidget(self.current_yarn_colour)
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

    def yarn_colour(self, yarn_no):
        yarn = self.yarns[yarn_no]
        if not self.yarnlock.isChecked():
            old_col = yarn.getColour()
            get_col = QColorDialog.getColor()
            if get_col.isValid():
                new_col=get_col.name()
                yarn.setColour(new_col)
                if old_col:
                    self.change_warp_colour(old_col, new_col)
        self.current_yarn_colour.setColour(yarn.getColour())
        self.current_yarn_colour.colour_index=yarn.colour_index

    def change_warp_colour(self, old_col, new_col):
        for warp in self.loom.warps:
            if warp.getColour() == old_col:
                warp.setColour(new_col)
            for row in self.loom.band:
                for pick in row:
                    if pick.getColour() == old_col:
                        pick.setColour(new_col)
                    if pick.getAltColour() == old_col:
                        pick.setAltColour(new_col)

    def add_warp_thread(self):
        try:
            loom_warp, band_warp = self.loom.add_new_warp(self.loom_frame, self.band_frame)
            loom_warp.clicked.connect(lambda: self.colour_warp_thread(loom_warp.warp_number))
            for pick in band_warp:
                pick.clicked.connect(
                    lambda checked=pick.isChecked(), i=pick.warp_number, j=pick.pick_number: self.pickup(i, j))
        except AttributeError:
            pass

    def remove_warp_thread(self):
        self.loom.remove_warp_thread()

    def colour_warp_thread(self, warp):
        this_warp = self.loom.warps[warp]
        col=self.current_yarn_colour.getColour()
        this_warp.setColour(col)
        try:
            prev_warp=self.loom.warps[warp-1]
            prev_colour=prev_warp.getColour()
        except IndexError:
            prev_colour=None
        try:
            next_warp=self.loom.warps[warp+1]
            next_colour=next_warp.getColour()
        except IndexError:
            next_colour=None

        for pick in self.loom.band[warp]:
            pick.setColour(col)
        try:
            if pick.isHeddled:
                for next_pick in self.loom.band[warp+1]:
                    next_pick.setAltColour(col)
                    pick.setAltColour(next_colour)
            else:
                for prev_pick in self.loom.band[warp-1]:
                    prev_pick.setAltColour(col)
                    pick.setAltColour(prev_colour)

        except IndexError:
            pass

    def get_next_colour(self):
        try:
            next_index_start=self.current_yarn_colour.colour_index+1
            for i in range(12):
                next_index= (next_index_start + i) % 12
                next_colour=self.yarns[next_index].getColour()
                if next_colour:
                    self.current_yarn_colour.setColour(next_colour)
                    self.current_yarn_colour.colour_index=next_index
                    break
        except TypeError:
            pass


    def pickup(self,warp_no,pick_no):
        if self.loom.band[warp_no][pick_no].getAltColour():
            self.loom.band[warp_no][pick_no].doPickup()

    def debug(self):
        for i in self.loom.band:
            for j in i:
                print(j.getColour(),j.getAltColour(), j.isHeddled)

if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    sys.exit(0)
