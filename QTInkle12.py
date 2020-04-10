#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QGridLayout, QColorDialog, QLabel, \
    QVBoxLayout, QHBoxLayout, QSpacerItem, QCheckBox, QMainWindow, QAction, QFileDialog, QMessageBox

from PySide2.QtGui import QFont, QIcon
from PySide2.QtCore import *
from guppy import hpy
from foreground import get_foreground
from functools import partial
import os.path
import inspect
import pickle
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
                            font: bold;
                            font-size: 36px;
                            }""")

        self.colour = self.palette().button().color().name()
        self.inital_colour = self.colour

    def setColour(self, col, *textcol):
        try:
            tcol = textcol[0] if textcol else 'black'
            s = "QPushButton {background-color: " + col + "; color: " + tcol + ";}"
            self.setStyleSheet(s)
            self.colour = col
        except TypeError:
            pass

    def getColour(self):
        return self.colour


class YarnPalette():
    def __init__(self, yarn_ct):
        self.yarns = []
        self.yarn_lock = False
        self.create_yarns(yarn_ct)
        self.current_yarn_index = 0


    def create_yarns(self, yarn_ct):
        for yarn_no in range(yarn_ct):
            yarn = self.Yarn()
            yarn.index = yarn_no
            self.yarns.append(yarn)

    def change_yarn_colour(self, x, yarn_lock):
        yarn = self.yarns[x]
        if not yarn_lock:
            dialog_col = QColorDialog.getColor()
            if dialog_col.isValid():
                new_col = dialog_col.name()
                yarn.setColour(new_col)
        self.yarns[self.current_yarn_index].clear_colour_marker()
        yarn.set_colour_marker()
        self.current_yarn_index = x

        # text_colour = get_foreground(yarn.getColour())
        # yarn.setColour(yarn.getColour(), text_colour)
        # yarn.setFont(self.checkFont)
        # self.yarns[self.current_yarn_index].setText('')
        # yarn.setText(u'\u2713')

    class Yarn(ColourButton):
        def __init__(self):
            ColourButton.__init__(self)
            self.index = None
            self.inuse = False
            self.checkFont = QFont()
            self.checkFont.setBold(True)
            self.checkFont.setPointSize(18)

        def reinitialise(self):
            self.setColour(self.inital_colour)
            self.inuse = False
            self.setText('')

        def set_colour_marker(self):
            text_colour = get_foreground(self.getColour())
            self.setColour(self.getColour(), text_colour)
            self.setFont(self.checkFont)
            self.setText(u'\u2713')

        def clear_colour_marker(self):
            self.setText('')

        def reload(self, load_data, current_yarn):
            self.setColour(load_data["colour"])
            self.inuse = load_data["inuse"]
            txt = u'\u2713' if self.index == current_yarn else ''
            self.setFont(self.checkFont)
            self.setText(txt)


class Loom():
    def __init__(self, max_warp_threads, pick_ct):
        self.warp_threads = []
        self.warp_thread_ct = 0
        self.max_warp_threads = max_warp_threads
        self.pick_ct = pick_ct

    def add_warp_thread(self):
        if self.warp_thread_ct < self.max_warp_threads:
            warp_thread = self.WarpThread(self.pick_ct)
            warp_thread.index = self.warp_thread_ct
            warp_thread.isHeddled = True if warp_thread.index % 2 == 0 else False
            self.warp_threads.append(warp_thread)
            self.set_alt_warp_threads()
            self.warp_thread_ct += 1
            return True
        else:
            return False

    def remove_warp_thread(self):
        if self.warp_thread_ct > 0:
            self.warp_thread_ct -= 1
            warp_thread = self.warp_threads[self.warp_thread_ct]
            for pick in warp_thread.picks:
                pick.setParent(None)
                # pick.deleteLater()
                del pick
            warp_thread.setParent(None)
            if not warp_thread.isHeddled:
                alt_heddled_thread = self.warp_threads[self.warp_thread_ct - 1]
                alt_heddled_thread.alt_warp_thread = None
                for pick in alt_heddled_thread.picks:
                    pick.set_display_colour(alt_heddled_thread, None)
            # warp.deleteLater()
            del warp_thread
            return True
        else:
            return False

    def set_alt_warp_threads(self):
        for warp_thread in self.warp_threads:
            alt_warp_thread_index = warp_thread.index + 1 if warp_thread.isHeddled else warp_thread.index - 1
            try:
                warp_thread.alt_warp_thread = self.warp_threads[alt_warp_thread_index]
            except IndexError:
                warp_thread.alt_warp_thread = None

    def reload(self, load_data, yarns):
        self.set_alt_warp_threads()
        for data in load_data:
            self.warp_threads[data["index"]].reload(data, yarns)
        for warp_thread in self.warp_threads:
            warp_thread.reload_pick_colours()

    def change_warp_colour(self, yarn):
        for warp_thread in self.warp_threads:
            if warp_thread.yarn_index == yarn.index:
                warp_thread.new_colour(yarn)

    class WarpThread(ColourButton):
        def __init__(self, pick_ct):
            ColourButton.__init__(self)
            self.index = None
            self.yarn_index = None
            self.alt_warp_thread = None
            self.isHeddled = True
            self.pick_ct = pick_ct
            self.picks = []
            for pick_no in range(self.pick_ct):
                pick = self.Pick()
                pick.index = pick_no
                self.picks.append(pick)

        def new_colour(self, yarn):
            self.yarn_index = yarn.index
            self.setColour(yarn.getColour())
            for pick in self.picks:
                pick.set_display_colour(self, self.alt_warp_thread)

        def toggle_pick(self, pick_index):
            self.picks[pick_index].toggle_pick(self, self.alt_warp_thread)

        def reintialise(self):
            self.setColour(self.inital_colour)
            self.yarn_index = None
            for pick in self.picks:
                pick.reinitialise()

        def reload(self, data, yarns):
            self.pick_ct = len(data["picks"])
            for pick in self.picks:
                pick.reload(data["picks"][pick.index])
            try:
                self.new_colour(yarns[data["yarn_index"]])
            except TypeError:
                self.setColour(self.inital_colour)

        def reload_pick_colours(self):
            for pick in self.picks:
                pick.set_display_colour(self, self.alt_warp_thread)

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
                        self.setColour(warp_thread.getColour())

            def toggle_pick(self, warp_thread, alt_warp_thread):
                self.isPicked = not self.isPicked
                self.set_display_colour(warp_thread, alt_warp_thread)

            def reinitialise(self):
                self.setColour(self.inital_colour)
                self.isPicked = False

            def reload(self, load_data):
                self.isPicked = load_data["isPicked"]


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle(os.path.splitext(os.path.basename(__file__))[0])
        self.add_menu()
        self.setFixedSize(1200, 700)
        self.titleFont = QFont()
        self.titleFont.setBold(True)
        self.titleFont.setPointSize(16)
        self.yarns = YarnPalette(12)
        for yarn in self.yarns.yarns:
            yarn.clicked.connect(
                lambda checked=yarn.isChecked(), x=yarn.index: self.change_yarn_colour(x, self.yarns.yarn_lock))
        self.current_yarn_index = None
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
        self.warp_thread_ct = 0
        self.initial_warp_ct = 12
        self.create_initial_warp(self.initial_warp_ct)

    def create_initial_warp(self, number_of_warps):
        for warp_no in range(number_of_warps):
            self.add_warp_thread(warp_no)

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
        for yarn in self.yarns.yarns:
            yarn.setFixedSize(35, 30)
            yarn_grid.addWidget(yarn)
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
        self.loom_add_warp_thread_btn.clicked.connect(lambda: self.add_warp_thread(self.warp_thread_ct))
        self.loom_remove_warp_thread_btn.setText("Thread -")
        self.loom_remove_warp_thread_btn.move(910, 40)
        self.loom_remove_warp_thread_btn.clicked.connect(lambda: self.remove_warp_thread())

    def design_band_frame(self):
        self.band_frame.setFrameShape(QFrame.StyledPanel)
        self.band_frame.setGeometry(0, 200, 1200, 500)
        self.band_title.setText("Band")
        self.band_title.setGeometry(600, 14, 200, 20)
        self.band_title.setFont(self.titleFont)

    def yarn_lock_changed(self, state):
        self.yarns.yarn_lock = True if state == Qt.Checked else False

    def change_yarn_colour(self, x, yarn_lock):
        self.yarns.change_yarn_colour(x, yarn_lock)
        self.loom.change_warp_colour(self.yarns.yarns[x])

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
        if self.loom.add_warp_thread():
            self.loom.warp_threads[warp_no].clicked.connect(
                lambda checked=self.loom.warp_threads[warp_no].isChecked(), x=warp_no: self.set_warp_colour(x))
            for pick in self.loom.warp_threads[warp_no].picks:
                pick.clicked.connect(
                    lambda checked=pick.isChecked(), x=warp_no, y=pick.index: self.pickup_single_thread(x, y))
            self.display_warp_thread(self.loom.warp_threads[warp_no])
            self.warp_thread_ct += 1

    def remove_warp_thread(self):
        if self.loom.remove_warp_thread():
            self.warp_thread_ct -= 1

    # def change_yarn_colour(self, yarn_no):
    #     clicked_yarn = self.yarns[yarn_no]
    #     if clicked_yarn.change_colour(self.yarn_lock.isChecked()):
    #         try:
    #             prev_yarn = self.yarns[self.current_yarn_index]
    #             prev_yarn.clear_colour_marker()
    #         except TypeError:
    #             pass
    #         clicked_yarn.set_colour_marker()
    #         self.current_yarn_index = yarn_no
    #         self.change_warp_colour(clicked_yarn)

    def set_warp_colour(self, clicked_warp_no):
        yarn = self.yarns.yarns[self.yarns.current_yarn_index]
        self.loom.warp_threads[clicked_warp_no].new_colour(yarn)

    def change_warp_colour(self, yarn):
        self.loom.change_warp_colour(yarn)

    def pickup_single_thread(self, warp_no, clicked_pick_no):
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
        for yarn in self.yarns:
            yarn.reload(load_yarns[yarn.index], self.current_yarn_index)
        while self.warp_thread_ct > load_thread_ct:
            self.remove_warp_thread()
        for warp_no in range(self.warp_thread_ct, load_thread_ct):
            self.add_warp_thread(warp_no)
        self.loom.reload(load_loom, self.yarns)
        self.warp_thread_ct = load_thread_ct

    def newCall(self):
        self.band_title.setText("Band")
        self.current_yarn_index = None
        self.yarn_lock.setChecked(False)
        for yarn in self.yarns:
            yarn.reinitialise()
        while self.warp_thread_ct > 12:
            self.remove_warp_thread()
        for warp_thread in self.loom.warp_threads:
            warp_thread.reintialise()
        for warp_no in range(self.warp_thread_ct, 12):
            self.add_warp_thread(warp_no)

    def saveCall(self):
        save_main = {"thread_ct": self.warp_thread_ct, "current_yarn": self.current_yarn_index,
                     "yarn_lock": self.yarn_lock.isChecked(), "title": self.band_title.text()}
        save_yarns = []
        for yarn in self.yarns:
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
        if self.is_saved:
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
    h = hpy()

    myApp = QApplication(sys.argv)
    window = Window()
    window.show()

    myApp.exec_()
    #    print(h.heap())
    #    print(h.heapu())
    sys.exit(0)
