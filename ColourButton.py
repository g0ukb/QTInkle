#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QPushButton
from PySide2.QtGui import QFont
from foreground import get_foreground
import sys


class ColourButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colour = self.palette().button().color().name()
        self.initial_colour = self.colour
        self.setColour(self.initial_colour)

    def setColour(self, col):
        try:
            tcol = get_foreground(col)
            s = """ QPushButton {                      
                               border - style: outset;
                               border - width: 50 px;
                               border - radius: 2000px;
                               border - color: white;
                               padding: 4 px;
                               font: 16pt;
              """
            s = s + "background-color:" + col + "; color: " + tcol + ";}"
            self.setStyleSheet(s)
            self.colour = col
        except TypeError:
            pass

    def getColour(self):
        return self.colour


class PickButton(ColourButton):
    def __init__(self):
        ColourButton.__init__(self)

    def setColour(self, col):
        try:
            tcol = get_foreground(col)
            s = """ QPushButton {                      
                                 border - style: outset;
                                 border - width: 50 px;
                                 border - radius: 2000px;
                                 border - color: white;
                                 font: 7pt;
                """
            s = s + "background-color:" + col + "; color: " + tcol + ";}"
            self.setStyleSheet(s)
            self.colour = col
        except TypeError:
            pass
