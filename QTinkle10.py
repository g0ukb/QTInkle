#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox

from PySide2.QtGui import QFont, qApp
from PySide2.QtCore import *
import inspect
import sys


def dump_args(func):
    """Decorator to print function call details - parameters names and effective values.
    """

    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ', '.join('{} = {!r}'.format(*item) for item in func_args.items())
        print(f'{func.__module__}.{func.__qualname__} ( {func_args_str} )')
        return func(*args, **kwargs)

    return wrapper


class ColourButton(QPushButton):
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

    def setColour(self, col):
        try:
            s = "background-color:" + col + ";"
            self.setStyleSheet(s)
            self.colour = col
        except TypeError:
            pass

    def getColour(self):
        return self.colour


class Yarn(ColourButton):
    def __init__(self):
        ColourButton.__init__(self)
        self.index = None


class Pick(ColourButton):
    def __init__(self):
        ColourButton.__init__(self)
        self.index = None
        self.isPicked = False

    def set_display_colour(self, warp_thread, alt_warp_thread):
        if not self.isPicked:
            self.setColour(warp_thread.getColour())
        else:
            try:
                self.setColour(alt_warp_thread.getColour())
            except AttributeError:
                pass

    def toggle_pick(self,warp_thread,alt_warp_thread):
        self.isPicked = not self.isPicked
        self.set_display_colour(warp_thread, alt_warp_thread)

class WarpThread(ColourButton):
    def __init__(self, pick_ct):
        ColourButton.__init__(self)
        self.index = None
        self.yarn_index = None
        self.alt_warp_thread = None
        self.isHeddled = True
        self.pick_ct = pick_ct
        self.picks = []
        for i in range(self.pick_ct):
            pick = Pick()
            pick.index = i
            self.picks.append(pick)

    def new_colour(self, yarn):
        self.yarn_index = yarn.yarn_index
        self.setColour(yarn.getColour())
        for pick in self.picks:
            pick.set_display_colour(self, self.alt_warp_thread)

    def toggle_pick(self, pick_index):

        self.picks[pick_index].toggle_pick(self, self.alt_warp_thread)

# todo = colour propogation when existing warp colour changes
# todo = clean up alt-warp when warp is deleted
# todo = BUG colour = none but alt-colour is OK, toggle shows alt_colour, toggle-back does not wipe alt-colour

class Warp():
    def __init__(self):
        self.warp_threads = []
        self.warp_thread_ct = 0
        self.pick_ct = 20

    def add_warp_thread(self):
        warp_thread = WarpThread(self.pick_ct)
        warp_thread.index = self.warp_thread_ct
        warp_thread.isHeddled = True if warp_thread.index % 2 == 0 else False
        self.warp_threads.append(warp_thread)
        self.set_alt_warp_thread()
        self.warp_thread_ct += 1

    def remove_warp_thread(self):
        if self.warp_thread_ct > 0:
            self.warp_thread_ct -= 1
            warp_thread = self.warp_threads[self.warp_thread_ct]
            for pick in warp_thread.picks:
                pick.setParent(None)
                # pick.deleteLater()
                del pick
            warp_thread.setParent(None)
            # warp.deleteLater()
            del warp_thread

    def set_alt_warp_thread(self):
        for warp_thread in self.warp_threads:
            alt_warp_thread_index = warp_thread.index + 1 if warp_thread.isHeddled else warp_thread.index - 1
            try:
                warp_thread.alt_warp_thread = self.warp_threads[alt_warp_thread_index]
            except IndexError:
                warp_thread.alt_warp_thread = None


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
        self.current_yarn_colour = ColourButton()
        self.current_yarn_index = None
        self.yarn_lock = QCheckBox("Lock Colours")
        self.yarn_frame = QFrame(self)
        self.design_yarn_frame()
        self.loom_frame = QFrame(self)
        self.loom_add_warp_thread_btn = QPushButton(self.loom_frame)
        self.loom_remove_warp_thread_btn = QPushButton(self.loom_frame)
        self.design_loom_frame()
        self.band_frame = QFrame(self)
        self.band_title = QLabel(self.band_frame)
        self.design_band_frame()
        self.warp = Warp()
        self.warp_thread_ct = 0
        self.create_initial_warp(12)

    def create_yarns(self):
        for i in range(12):
            yarn = Yarn()
            yarn.yarn_index = i
            self.yarns.append(yarn)
            self.yarns[i].clicked.connect(
                lambda checked=self.yarns[i].isChecked(), x=i: self.change_yarn_colour(x))

    def create_initial_warp(self, number_of_warps):
        for i in range(number_of_warps):
            self.add_warp_thread(i)

    def design_yarn_frame(self):
        self.yarn_frame.setFrameShape(QFrame.StyledPanel)
        self.yarn_frame.setGeometry(0, 0, 200, 200)
        yarn_box = QVBoxLayout()
        title = QLabel("Yarns")
        title.setFont(self.titleFont)
        title.setAlignment(Qt.AlignCenter)
        yarn_box.addWidget(title)
        yarn_grid = QGridLayout()
        yarn_grid.setColumnStretch(1, 4)
        yarn_grid.setColumnStretch(2, 4)
        yarn_grid.setColumnStretch(3, 4)
        for i in range(12):
            yarn_grid.addWidget(self.yarns[i])
        yarn_box.addLayout(yarn_grid)
        yarn_lock_box = QHBoxLayout()
        yarn_lock_box.addWidget(self.yarn_lock)
        yarn_box.addLayout(yarn_lock_box)
        current_yarn_box = QHBoxLayout()
        current_yarn_box.addWidget(QLabel("Current"))
        current_yarn_box.addWidget(self.current_yarn_colour)
        current_yarn_box.insertSpacing(40, 40)
        yarn_box.addLayout(current_yarn_box)
        self.yarn_frame.setLayout(yarn_box)

    def design_loom_frame(self):
        self.loom_frame.setFrameShape(QFrame.StyledPanel)
        self.loom_frame.setGeometry(200, 0, 1000, 200)
        title = QLabel(self.loom_frame)
        title.setText("Loom")
        title.setGeometry(400, 14, 200, 20)
        title.setFont(self.titleFont)
        self.loom_add_warp_thread_btn.setText("Thread +")
        self.loom_add_warp_thread_btn.move(10, 40)
        self.loom_add_warp_thread_btn.clicked.connect(lambda: self.add_warp_thread(self.warp_ct))
        self.loom_remove_warp_thread_btn.setText("Thread -")
        self.loom_remove_warp_thread_btn.move(910, 40)
        self.loom_remove_warp_thread_btn.clicked.connect(lambda: self.remove_warp_thread())

    def design_band_frame(self):
        self.band_frame.setFrameShape(QFrame.StyledPanel)
        self.band_frame.setGeometry(0, 200, 1200, 500)
        self.band_title.setText("Band")
        self.band_title.setGeometry(600, 14, 200, 20)
        self.band_title.setFont(self.titleFont)

    def display_warp_thread(self, warp_thread):
        warp_thread.resize(10, 30)
        x_offset = 100
        y_offset = 80
        warp_thread.setParent(self.loom_frame)
        y = y_offset if warp_thread.isHeddled else y_offset + 30
        warp_thread.move(x_offset + warp_thread.index * 10, y)
        warp_thread.show()
        for pick in warp_thread.picks:
            pick.resize(28, 11)
            x_offset = 20
            y_offset = 50
            pick.setParent(self.band_frame)
            x = x_offset if warp_thread.isHeddled else x_offset + 29
            y = y_offset if warp_thread.isHeddled else y_offset + 5
            pick.move(x + 58 * pick.index, y + 11 * (warp_thread.index // 2))
            pick.show()

    def add_warp_thread(self, warp_no):
        self.warp.add_warp_thread()
        self.warp.warp_threads[warp_no].clicked.connect(
            lambda checked=self.warp.warp_threads[warp_no].isChecked(), x=warp_no: self.change_warp_colour(x))
        for pick_no, pick in enumerate(self.warp.warp_threads[warp_no].picks):
            pick.clicked.connect(lambda checked=pick.isChecked(), x=warp_no, y=pick_no: self.do_single_pick(x, y))
        self.display_warp_thread(self.warp.warp_threads[warp_no])
        self.warp_thread_ct += 1

    def remove_warp_thread(self):
        self.warp.remove_warp_thread()
        self.warp_thread_ct -= 1

    def change_yarn_colour(self, index):
        yarn = self.yarns[index]
        if not self.yarn_lock.isChecked():
            get_col = QColorDialog.getColor()
            if get_col.isValid():
                new_col = get_col.name()
                yarn.setColour(new_col)
        self.current_yarn_colour.setColour(yarn.getColour())
        self.current_yarn_index = yarn.yarn_index

    def change_warp_colour(self, index):
        #try:
            yarn = self.yarns[self.current_yarn_index]
            self.warp.warp_threads[index].new_colour(yarn)
        #except TypeError:
        #    pass

    def do_single_pick(self, i, j):
        self.warp.warp_threads[i].toggle_pick(j)


if __name__ == '__main__':
    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    sys.exit(0)
