#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox, QMainWindow, QAction, QFileDialog, QMessageBox

from PySide2.QtGui import QFont, QIcon
from PySide2.QtCore import *
#from guppy import hpy
from foreground import get_foreground
from functools import partial
import os.path
import inspect
import pickle
import sys
from YarnPalette import YarnPalette
from Loom import Loom


def dump_args(func):
    """Decorator to print function call details - parameters names and effective values.
    """

    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ', '.join('{} = {!r}'.format(*item) for item in func_args.items())
        print(f'{func.__module__}.{func.__qualname__} ( {func_args_str} )')
        return func(*args, **kwargs)

    return wrapper








class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle(os.path.splitext(os.path.basename(__file__))[0])
        self.add_menu()
        self.setFixedSize(1200, 700)
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSize(16)
        self.yarnpalette = YarnPalette(12)
        self.yarn_lock = QCheckBox("Lock Colours")
        self.yarn_lock.stateChanged.connect(self.yarn_lock_changed)
        self.yarn_frame = QFrame(self)
        self.design_yarn_frame()
        self.loom_frame = QFrame(self)
        self.loom_add_warp_thread_btn = QPushButton(self.loom_frame)
        self.loom_remove_warp_thread_btn = QPushButton(self.loom_frame)
        self.design_loom_frame()
        self.band_frame = QFrame(self)
        self.band_title = QLabel(self.band_frame)
        self.design_band_frame()
        self.loom = Loom(80, 20)
        for warp_thread in self.loom.warp_threads:
            self.display_warp_thread(warp_thread)

    def design_yarn_frame(self):
        self.yarn_frame.setFrameShape(QFrame.StyledPanel)
        self.yarn_frame.setGeometry(0, 20, 200, 180)
        yarn_box = QVBoxLayout()
        title = QLabel("Yarns")
        title.setFont(self.titleFont)
        title.setAlignment(Qt.AlignCenter)
        yarn_box.addWidget(title)
        yarn_grid = QGridLayout()
        yarn_grid.setColumnStretch(1, 4)
        yarn_grid.setColumnStretch(2, 4)
        yarn_grid.setColumnStretch(3, 4)
        for yarn in self.yarnpalette.yarns:
            yarn.setFixedSize(35, 30)
            yarn_grid.addWidget(yarn)
            yarn.clicked.connect(
                lambda checked=yarn.isChecked(), y=yarn: self.yarn_clicked(y, self.yarnpalette.yarn_lock))
        yarn_box.addLayout(yarn_grid)
        yarn_lock_box = QHBoxLayout()
        yarn_lock_box.addWidget(self.yarn_lock)
        yarn_box.addLayout(yarn_lock_box)
        self.yarn_frame.setLayout(yarn_box)

    def design_loom_frame(self):
        self.loom_frame.setFrameShape(QFrame.StyledPanel)
        self.loom_frame.setGeometry(200, 20, 1000, 180)
        title = QLabel(self.loom_frame)
        title.setText("Loom")
        title.setGeometry(400, 14, 200, 20)
        title.setFont(self.titleFont)
        self.loom_add_warp_thread_btn.setText("Thread +")
        self.loom_add_warp_thread_btn.move(10, 40)
        self.loom_add_warp_thread_btn.clicked.connect(lambda: self.add_warp_thread_clicked())
        self.loom_remove_warp_thread_btn.setText("Thread -")
        self.loom_remove_warp_thread_btn.move(910, 40)
        self.loom_remove_warp_thread_btn.clicked.connect(lambda: self.remove_warp_thread_clicked())

    def design_band_frame(self):
        self.band_frame.setFrameShape(QFrame.StyledPanel)
        self.band_frame.setGeometry(0, 200, 1200, 500)
        self.band_title.setText("Band")
        self.band_title.setGeometry(600, 14, 200, 20)
        self.band_title.setFont(self.titleFont)

    def display_warp_thread(self, warp_thread):
        warp_thread.setParent(self.loom_frame)
        warp_thread.clicked.connect(
            lambda checked=warp_thread.isChecked(), x=warp_thread.index: self.warp_thread_clicked(x))
        for pick in warp_thread.picks:
            pick.clicked.connect(
                lambda checked=pick.isChecked(), x=warp_thread.index, y=pick.index: self.pickup_clicked(x, y))
        if warp_thread:
            warp_thread.resize(10, 30)
            x_offset = 100
            y_offset = 80
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


    def yarn_lock_changed(self, state):
        self.yarnpalette.yarn_lock = True if state == Qt.Checked else False

    def yarn_clicked(self, yarn, yarn_lock):
        self.yarnpalette.change_yarn_colour(yarn, yarn_lock)
        self.loom.change_warp_colour(yarn)  # todo - alt yarns not being changed
        #self.loom.change_warp_colour(self.yarnpalette.yarns[yarn.index])

    def add_warp_thread_clicked(self):
        warp_thread = self.loom.add_warp_thread()
        if warp_thread:
            self.display_warp_thread(warp_thread)

    def remove_warp_thread_clicked(self):
        self.loom.remove_warp_thread()

    def warp_thread_clicked(self, clicked_warp_no):
        yarn = self.yarnpalette.yarns[self.yarnpalette.current_yarn_index]
        self.loom.warp_threads[clicked_warp_no].new_colour(yarn)

    def pickup_clicked(self, warp_no, clicked_pick_no):
        self.loom.warp_threads[warp_no].toggle_pick(clicked_pick_no)

    def add_menu(self):
        newAction = QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New document')
        newAction.triggered.connect(self.newCall)

        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.openCall)

        saveAction = QAction('&Save', self)
        saveAction.setShortcut('Ctrl+O')
        saveAction.setStatusTip('Save design')
        saveAction.triggered.connect(self.saveCall)

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        printMenu = menuBar.addMenu('&Print')

    def openCall(self):
        picklefile, _ = QFileDialog().getOpenFileName(self, "Load Inkle Pattern", "./Patterns",
                                                      "Inkle Pattern Files (*.ik2)",
                                                      options=QFileDialog.DontUseNativeDialog)
        load_dump = pickle.load(open(picklefile, "rb"))
        load_main = load_dump["save_main"]
        load_yarns = load_dump["save_yarns"]
        load_loom = load_dump["save_loom"]
        self.band_title = load_main["title"]
        self.current_yarn_index = load_main["current_yarn"]
        self.yarn_lock.setChecked(load_main["yarn_lock"])
        load_thread_ct = load_main["thread_ct"]
        for yarn in self.yarnpalette:
            yarn.reload(load_yarns[yarn.index], self.current_yarn_index)
        while self.warp_thread_ct > load_thread_ct:
            self.remove_warp_thread()
        for warp_no in range(self.warp_thread_ct, load_thread_ct):
            self.add_warp_thread_clicked(warp_no)
        self.loom.reload(load_loom, self.yarnpalette)
        self.warp_thread_ct = load_thread_ct

    def newCall(self):
        self.band_title.setText("Band")
        self.current_yarn_index = None
        self.yarn_lock.setChecked(False)
        for yarn in self.yarnpalette:
            yarn.reinitialise()
        while self.warp_thread_ct > 12:
            self.remove_warp_thread()
        for warp_thread in self.loom.warp_threads:
            warp_thread.reintialise()
        for warp_no in range(self.warp_thread_ct, 12):
            self.add_warp_thread_clicked(warp_no)

    def saveCall(self):
        save_main = {"thread_ct": self.warp_thread_ct, "current_yarn": self.current_yarn_index,
                     "yarn_lock": self.yarn_lock.isChecked(), "title": self.band_title.text()}
        save_yarns = []
        for yarn in self.yarnpalette:
            yarn_info = {"index": yarn.index, "colour": yarn.getColour(), "inuse": yarn.inuse}
            save_yarns.append(yarn_info)
        save_loom = []
        for warp_thread in self.loom.warp_threads:
            save_warp = {"index": warp_thread.index, "yarn_index": warp_thread.yarn_index}
            save_picks = []
            for pick in warp_thread.picks:
                save_pick = {"index": pick.index, "isPicked": pick.isPicked}
                save_picks.append(save_pick)
            save_warp['picks'] = save_picks
            save_loom.append(save_warp)
        save_dump = {"save_main": save_main, "save_yarns": save_yarns, "save_loom": save_loom}
        picklefile, _ = QFileDialog().getSaveFileName(self, "Save Inkle Pattern", "./Patterns",
                                                      "Inkle Pattern Files (*.ik2)",
                                                      options=QFileDialog.DontUseNativeDialog)
        pickle.dump(save_dump, open(picklefile + '.ik2', "wb"))

    def exitCall(self):
        print('Exit app')

    def closeEvent(self, event):
        if self.yarnpalette.is_modified or self.loom.is_modified:
            event.accept()
        else:
            popup = QMessageBox(self)
            popup.setIcon(QMessageBox.Warning)
            popup.setText('The settings have been changed')
            popup.setInformativeText('Do you want to save the changes or discard them?')
            popup.setStandardButtons(QMessageBox.Save |
                                     QMessageBox.Discard |
                                     QMessageBox.Cancel)

            popup.setDefaultButton(QMessageBox.Save)
            answer = popup.exec_()
            if answer == QMessageBox.Save:
                self.save_settings()
                event.accept()
            elif answer == QMessageBox.Discard:
                self.load_settings()
                self.is_saved = True
                event.accept()
            elif answer == QMessageBox.Cancel:
                event.ignore()

        self.ui.statusLabel.clear()


if __name__ == '__main__':
#    h = hpy()

    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    #    print(h.heap())
    #    print(h.heapu())
    sys.exit(0)
