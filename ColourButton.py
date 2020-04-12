#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import  QPushButton


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
