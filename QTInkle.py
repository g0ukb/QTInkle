#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox, QMainWindow, QAction, QFileDialog, QMessageBox, QSpinBox

from PySide2.QtGui import QFont, QPixmap
from PySide2.QtCore import *
# from guppy import hpy
import os.path
import inspect
import pickle
import sys
from functools import partial
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


def dump_func_name(func):
    def echo_func(*func_args, **func_kwargs):
        print('')
        print('Start func: {}'.format(func.__name__))
        return func(*func_args, **func_kwargs)

    return echo_func


def get_html_colour(bgr_decimal):
    hex_colour_bgr = format(bgr_decimal, '06x')
    return f"#{''.join([hex_colour_bgr[4:], hex_colour_bgr[2:4], hex_colour_bgr[:2]])}"


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle(os.path.splitext(os.path.basename(__file__))[0])
        self.setFixedSize(1200, 700)
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSize(16)
        self.add_menu()
        self.yarnpalette = YarnPalette(12)
        self.yarn_lock = QCheckBox("Lock Colours")
        self.yarn_lock.stateChanged.connect(self.yarn_lock_changed)
        self.yarn_frame = QFrame(self)
        self.design_yarn_frame()
        self.initial_warp_ct = 12
        self.loom_frame = QFrame(self)
        self.design_loom_frame()
        self.band_frame = QFrame(self)
        self.band_title = QLabel(self.band_frame)
        self.design_band_frame()
        self.loom = Loom(80, 20, self.initial_warp_ct)
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
        self.loom_warp_counter = QSpinBox(self.loom_frame)
        self.loom_warp_counter.setFont(self.titleFont)
        self.loom_warp_counter.move(500, 40)
        self.loom_warp_counter.setRange(0, 80)
        self.loom_warp_counter.setValue(self.initial_warp_ct)
        self.loom_warp_counter.setStyleSheet("QSpinBox{font-weight: normal; font-size:14pt; font-family: Helvetica;}")
        self.loom_warp_counter.valueChanged.connect(
            lambda: self.warp_counter_changed())

    def design_band_frame(self):
        self.band_frame.setFrameShape(QFrame.StyledPanel)
        self.band_frame.setGeometry(0, 200, 1200, 500)
        self.band_title.setText("Band")
        self.band_title.setGeometry(600, 14, 200, 20)
        self.band_title.setFont(self.titleFont)

    def display_warp_thread(self, warp_thread):
        warp_thread.clicked.connect(
            lambda checked=warp_thread.isChecked(), x=warp_thread.index: self.warp_thread_clicked(x))
        for pick in warp_thread.picks:
            pick.clicked.connect(
                lambda checked=pick.isChecked(), x=warp_thread.index, y=pick.index: self.pickup_clicked(x, y))
        warp_thread.setParent(self.loom_frame)
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

    def yarn_clicked(self, yarn, yarn_lock):
        new_col = None
        if not yarn_lock:
            dialog_col = QColorDialog.getColor()
            if dialog_col.isValid():
                new_col = dialog_col.name()
        self.yarnpalette.change_yarn(yarn, new_col)
        self.loom.change_warp_yarn(yarn)

    def warp_thread_clicked(self, clicked_warp_no):
        yarn = self.yarnpalette.yarns[self.yarnpalette.current_yarn_index]
        self.loom.warp_threads[clicked_warp_no].change_yarn(yarn)

    def pickup_clicked(self, warp_no, clicked_pick_no):
        self.loom.warp_threads[warp_no].toggle_pick(clicked_pick_no)

    def yarn_lock_changed(self, state):
        self.yarnpalette.yarn_lock = True if state == Qt.Checked else False

    def warp_counter_changed(self):
        self.warp_size_changed(self.loom.warp_thread_ct, self.loom_warp_counter.value())

    def warp_size_changed(self, old_size, new_size):
        while old_size < new_size:
            self.add_warp_thread()
            old_size += 1
        while old_size > new_size:
            self.remove_warp_thread()
            old_size -= 1

    def add_warp_thread(self):
        warp_thread = self.loom.add_warp_thread()
        if warp_thread:
            self.display_warp_thread(warp_thread)

    def remove_warp_thread(self):
        self.loom.remove_warp_thread()

    def add_menu(self):
        newAction = QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New design')
        newAction.triggered.connect(partial(self.modified_check, self.newCall, lambda: None))
        #        newAction.triggered.connect(self.modified_check(self.newCall,lambda: None))

        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open design')
        openAction.triggered.connect(partial(self.modified_check, self.openCall, lambda: None))

        saveAction = QAction('&Save', self)
        saveAction.setShortcut('Ctrl+O')
        saveAction.setStatusTip('Save design')
        saveAction.triggered.connect(self.saveCall)

        importAction = QAction('&Import', self)
        importAction.setShortcut('Ctrl+I')
        importAction.setStatusTip('Import old .ikl design')
        importAction.triggered.connect(partial(self.modified_check, self.importCall, lambda: None))

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        printAction = QAction('&Print', self)
        printAction.setShortcut('Ctrl+P')
        printAction.setStatusTip('Print band')
        printAction.triggered.connect(self.printCall)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(importAction)
        fileMenu.addAction(exitAction)
        printMenu = menuBar.addMenu('&Print')
        printMenu.addAction(printAction)

    def modified_check(self, action, inaction):
        action()
        return
        if self.yarnpalette.is_modified or self.loom.is_modified:
            msg = QMessageBox(self)
            msg.setWindowTitle("Not Saved")
            msg.setText("Current work not saved")
            msg.setInformativeText("Continue?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            response = msg.exec_()
            msg.close()
            if response == QMessageBox.Yes:
                action()
            else:
                inaction()
        else:
            action()

    def openCall(self):
        picklefile, _ = QFileDialog().getOpenFileName(self, "Load Inkle Pattern", "./Patterns",
                                                      "Inkle Pattern Files (*.ik2)",
                                                      options=QFileDialog.DontUseNativeDialog)
        load_dump = pickle.load(open(picklefile, "rb"))
        load_main = load_dump["save_main"]
        load_yarns = load_dump["save_yarns"]
        load_loom = load_dump["save_loom"]
        # print(load_loom)
        #       self.band_title = load_main["title"]
        self.yarnpalette.load(load_yarns)
        self.yarn_lock.setChecked(self.yarnpalette.yarn_lock)
        self.warp_size_changed(self.loom_warp_counter.value(), load_loom["warp_thread_ct"])
        self.loom_warp_counter.setValue(load_loom["warp_thread_ct"])
        self.loom.load(load_loom)

    def newCall(self):
        self.band_title.setText("Band")
        self.loom_warp_counter.setValue(self.initial_warp_ct)
        self.yarn_lock.setChecked(False)
        self.yarnpalette.reset()
        self.warp_size_changed(self.loom.warp_thread_ct, self.initial_warp_ct)
        self.loom.reset(self.initial_warp_ct)

    def saveCall(self):
        save_main = {}
        save_yarns = self.yarnpalette.save()
        save_loom = self.loom.save()
        save_dump = {"save_main": save_main, "save_yarns": save_yarns, "save_loom": save_loom}
        picklefile, _ = QFileDialog().getSaveFileName(self, "Save Inkle Pattern", "./Patterns",
                                                      "Inkle Pattern Files (*.ik2)",
                                                      options=QFileDialog.DontUseNativeDialog)
        pickle.dump(save_dump, open(picklefile + '.ik2', "wb"))

    def importCall(self):
        importfile, _ = QFileDialog().getOpenFileName(self, "Load Inkle Pattern", "./Patterns",
                                                      "Inkle Pattern Files (*.ikl)",
                                                      options=QFileDialog.DontUseNativeDialog)
        with open(importfile, 'r') as f:
            lines = f.read().splitlines()
        old_keys = ['version', 'name', 'notes', 'pattern_thread', 'ground_thread', 'pick_ct', 'warp_pair_ct', 'mode',
                    'pattern_colour', 'ground_colour', 'font_colour', 'pattern_shift', 'pattern']
        try:
            version = lines[0]
            assert version == 'V1.02'
            old_data = dict(zip(old_keys[:-1], lines[:11]))
            old_data['pattern'] = lines[12:-2]
            print(old_data)
        except AssertionError:
            print("Invalid file - ignoring")
            return
        load_main = {}
        load_yarns = {"yarn_lock": True, "is_modified": False, "current_yarn_index": 0}
        yarns = [{"colour": get_html_colour(int(old_data["ground_colour"]))},
                 {"colour": get_html_colour(int(old_data["pattern_colour"]))}]
        col = self.yarnpalette.yarns[0].initial_colour
        for _ in range(10):
            yarns.append({"colour": col})
        load_yarns["yarns"] = yarns
        self.yarnpalette.load(load_yarns)
        self.yarn_lock.setChecked(self.yarnpalette.yarn_lock)
        warp_pair_ct = int(old_data["warp_pair_ct"])
        load_loom = {'warp_thread_ct': warp_pair_ct * 2, "is_modified": False}
        warp_threads = []
        for i in range(warp_pair_ct):
            pattern_row = lines[12 + i]
            p = [[int(a + b) for a, b in zip(pattern_row[::4], pattern_row[1::4])],
                 [int(a + b) for a, b in zip(pattern_row[2::4], pattern_row[3::4])]]
            warp_pair = [{"index": i * 2, "pickup_warp_index": i * 2 + 1},
                         {"index": i * 2 + 1, "pickup_warp_index": i * 2}]
            for j in range(2):
                if p[j][0] == 51 or p[j][0] == 48:
                    warp_pair[j]["yarn_index"] = 0
                    warp_pair[j]["colour"] = get_html_colour(int(old_data["ground_colour"]))
                else:
                    warp_pair[j]["yarn_index"] = 1
                    warp_pair[j]["colour"] = get_html_colour(int(old_data["pattern_colour"]))
                warp_pair[j]["pick_data"] = []
                for k in range(self.loom.pick_ct):
                    try:
                        d = {"isPicked": p[j][k] < 50}
                        warp_pair[j]["pick_data"].append(d)
                    except IndexError:
                        warp_pair[j]["pick_data"].append({"isPicked": False})
                warp_threads.append(warp_pair[j])
        load_loom['warp_threads'] = warp_threads
        print(load_loom)
        self.loom_warp_counter.setValue(warp_pair_ct * 2)
        self.warp_size_changed(self.loom.warp_thread_ct, self.loom_warp_counter.value())
        self.loom.load(load_loom)

    def exitCall(self):
        self.close()

    def closeEvent(self, event):
        self.modified_check(event.accept, event.ignore)

    def printCall(self):
        sshot = QPixmap.grabWidget(self)
        sshot.save('sshot.png')


if __name__ == '__main__':
    #    h = hpy()
    myApp = QApplication(sys.argv)
    window = Window()
    window.show()
    myApp.exec_()
    #    print(h.heap())
    #    print(h.heapu())
    sys.exit(0)
