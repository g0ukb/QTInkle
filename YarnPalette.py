#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtGui import QFont
from ColourButton import ColourButton


class YarnPalette():
    def __init__(self, yarn_ct):
        self.yarns = []
        self.yarn_lock = False
        self.is_modified = False
        self.current_yarn_index = 0
        self.create_yarns(yarn_ct)

    def create_yarns(self, yarn_ct):
        for yarn_no in range(yarn_ct):
            yarn = self.Yarn()
            yarn.index = yarn_no
            self.yarns.append(yarn)

    def change_yarn_colour(self, yarn, yarn_lock):
        if not yarn_lock:
            dialog_col = QColorDialog.getColor()
            if dialog_col.isValid():
                new_col = dialog_col.name()
                yarn.setColour(new_col)
        self.yarns[self.current_yarn_index].clear_colour_marker()
        yarn.set_colour_marker()
        self.current_yarn_index = yarn.index
        self.is_modified = True

    class Yarn(ColourButton):
        def __init__(self):
            ColourButton.__init__(self)
            self.index = None
            self.checkFont = QFont()
            self.checkFont.setBold(True)
            self.checkFont.setPointSize(18)

        def reinitialise(self):
            self.setColour(self.inital_colour)
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
            txt = u'\u2713' if self.index == current_yarn else ''
            self.setFont(self.checkFont)
            self.setText(txt)
