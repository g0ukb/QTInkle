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
        self.colour = "White"
        self.yarn_index = 0


    def setColour(self, col):
        self.colour = col
        self.updateColour(col)

    def updateColour(self, col):
        try:
            s = "background-color:" + col + ";"
            self.setStyleSheet(s)
        except TypeError:
            pass



class Warp(Yarn):
    def __init__(self, parent, i):
        Yarn.__init__(self, parent)
        self.warp_index=0
        self.paired_yarn_index=0
        self.isHeddled = not bool(self.index % 2)

    def setColour(self, col):
        col=yarns[]
        self.colour = col
        self.colour_index
        self.updateColour(col)


class Pick(Warp):
    def __init__(self, parent, i,j):
        Warp.__init__(self, parent,i)
        self.warp_index=i
        self.pick_index=j
        self.isPicked=False

    def doPickup(self):
        self.isPicked = not self.isPicked
        self.swapPickColour()

    def swapPickColour(self):
          col = self.paired_warp_colour if self.isPicked else self.colour
          self.updateColour(col)




# class SingleWarp(Yarn):
#     def __init__(self, parent, warp_no):
#         Yarn.__init__(self, parent)
#         self.warp_number = warp_no
#         self.isHeddled = not bool(warp_no % 2)
#         self.alt_colour_index = 0
#
#
# class SinglePick(SingleWarp):
#     def __init__(self, parent, warp_no):
#         SingleWarp.__init__(self, parent, warp_no)
#         self.isPicked = False
#         self.pick_number = 0
#


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
        new_warp_thread = Warp(parent,warp_no)
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
        pick_no = 0
        for pick in range(self.max_picks):
            new_pick = Pick(parent, warp_no,pick_no)
            new_pick.resize(29, 11)
            x = x_offset if new_pick.isHeddled else x_offset + 29
            y = y_offset if new_pick.isHeddled else y_offset + 5
            new_pick.move(x + 58 * pick, y + 11 * (warp_no // 2))
            new_pick.show()
            band_row.append(new_pick)
            pick_no += 1
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
        self.yarns = []
        self.create_yarns()
        self.current_yarn_colour = Yarn()
        self.current_yarn_colour.clicked.connect(lambda: self.get_next_colour())
        #self.current_yarn_colour.clicked.connect(lambda: self.debug())
        self.yarnlock = QCheckBox("Lock Colours")
        self.yarn_frame = QFrame(self)
        self.design_yarn_frame()
        self.loom_frame = QFrame(self)
        self.loom_add_warp_btn = QPushButton(self.loom_frame)
        self.loom_remove_warp_btn = QPushButton(self.loom_frame)
        self.design_loom_frame()
        self.band_frame = QFrame(self)
        self.band_title = QLabel(self.band_frame)
        self.design_band_frame()
        self.loom = Loom(self.loom_frame, self.band_frame, 6)
        # for warp in self.loom.warps:
        #     warp.clicked.connect(lambda checked=warp.isChecked(), i=warp.index: self.colour_warp_thread(i))
        # for band_row in self.loom.band:
        #     for pick in band_row:
        #         pick.clicked.connect(
        #             lambda checked=pick.isChecked(), i=pick.warp_index, j=pick.pick_index: self.pickup(i, j))

    def create_yarns(self):
        for i in range(12):
            yarn = Yarn()
            yarn.index=i
            self.yarns.append(yarn)
            self.yarns[i].clicked.connect(
                lambda checked=self.yarns[i].isChecked(), x=i: self.change_yarn_colour(x))


    def design_yarn_frame(self):
        self.yarn_frame.setFrameShape(QFrame.StyledPanel)
        self.yarn_frame.setGeometry(0, 0, 200, 200)
        yarnbox = QVBoxLayout()
        title = QLabel("Yarns")
        title.setFont(self.titleFont)
        title.setAlignment(Qt.AlignCenter)
        yarnbox.addWidget(title)
        yarngrid = QGridLayout()
        yarngrid.setColumnStretch(1, 4)
        yarngrid.setColumnStretch(2, 4)
        yarngrid.setColumnStretch(3, 4)
        for i in range(12):
            yarngrid.addWidget(self.yarns[i])
        yarnbox.addLayout(yarngrid)
        lockbox = QHBoxLayout()
        lockbox.addWidget(self.yarnlock)
        yarnbox.addLayout(lockbox)
        curbox = QHBoxLayout()
        curbox.addWidget(QLabel("Current"))
        curbox.addWidget(self.current_yarn_colour)
        curbox.insertSpacing(40, 40)
        yarnbox.addLayout(curbox)
        self.yarn_frame.setLayout(yarnbox)

    def design_loom_frame(self):
        self.loom_frame.setFrameShape(QFrame.StyledPanel)
        self.loom_frame.setGeometry(200, 0, 1000, 200)
        title = QLabel(self.loom_frame)
        title.setText("Loom")
        title.setGeometry(400, 14, 200, 20)
        title.setFont(self.titleFont)
        self.loom_add_warp_btn.setText("Thread +")
        self.loom_add_warp_btn.move(10, 40)
        self.loom_add_warp_btn.clicked.connect(lambda: self.add_warp_thread())
        self.loom_remove_warp_btn.setText("Thread -")
        self.loom_remove_warp_btn.move(910, 40)
        self.loom_remove_warp_btn.clicked.connect(lambda: self.remove_warp_thread())

    def design_band_frame(self):
        self.band_frame.setFrameShape(QFrame.StyledPanel)
        self.band_frame.setGeometry(0, 200, 1200, 500)
        self.band_title.setText("Band")
        self.band_title.setGeometry(600, 14, 200, 20)
        self.band_title.setFont(self.titleFont)



    def change_yarn_colour(self, yarn_no):
        yarn = self.yarns[yarn_no]
        if not self.yarnlock.isChecked():
            get_col = QColorDialog.getColor()
            if get_col.isValid():
                new_col = get_col.name()
                yarn.setColour(new_col)
                self.change_warp_yarn(yarn_no)
                self.current_yarn_colour.setColour(yarn.colour)
                self.current_yarn_colour.colour_index = yarn.colour_index

    def change_warp_yarn(self, index):
        colour=self.yarns[index].colour
        for warp in self.loom.warps:
            if warp.colour_index==index:
                warp.setColour(colour)
            for row in self.loom.band:
                for pick in row:
                    if pick.colour_index == index:
                        pick.setColour(colour)

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
        col = self.current_yarn_colour.getColour()
        this_warp.setColour(col)
        try:
            if this_warp.isHeddled:
                paired_warp=self.looms[warp+1]
            else:
                paired_warp=self.looms[warp-1]
            this_warp.altColour=paired_warp.colour
            paired_warp.altColour=this_warp.setColour
        except IndexError:
            pass
        for pick in self.loom.band[warp]:
            pick.setColour(col)

    def get_next_colour(self):
        try:
            next_index_start = self.current_yarn_colour.colour_index + 1
            for i in range(12):
                next_index = (next_index_start + i) % 12
                next_colour = self.yarns[next_index].colour
                if next_colour:
                    self.current_yarn_colour.setColour(next_colour)
                    self.current_yarn_colour.colour_index = next_index
                    break
        except TypeError:
            pass

    def pickup(self, warp_no, pick_no):
        self.loom.band[warp_no][pick_no].doPickup()

    def debug(self):
        for i in self.loom.band:
            for j in i:
                print(j.colour, j.altColour, j.isHeddled)


if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    sys.exit(0)
