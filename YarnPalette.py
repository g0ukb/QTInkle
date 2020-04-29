#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from PySide2.QtWidgets import QColorDialog

from foreground import get_foreground
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
            yarn = Yarn()
            yarn.index = yarn_no
            self.yarns.append(yarn)

    def change_yarn(self, yarn, new_col):
        if new_col:
            yarn.setColour(new_col)
        self.yarns[self.current_yarn_index].clear_current_marker()
        yarn.set_current_marker()
        self.current_yarn_index = yarn.index
        self.is_modified = True


    def reset(self):
        self.yarn_lock = False
        self.is_modified = False
        self.current_yarn_index = 0
        for yarn in self.yarns:
            yarn.reset()

    def save(self):
        save_data={"yarn_lock":self.yarn_lock, "is_modified":self.is_modified,"current_yarn_index":self.current_yarn_index}
        save_yarns=[yarn.save() for yarn in self.yarns]
        save_data["yarns"]=save_yarns
        return save_data

    def load(self,load_data):
        self.yarn_lock=load_data["yarn_lock"]
        self.is_modified=load_data["is_modified"]
        self.current_yarn_index = load_data["current_yarn_index"]
        for yarn, yarn_data in zip(self.yarns,load_data["yarns"]):
            yarn.load(yarn_data,self.yarns[self.current_yarn_index])



class Yarn(ColourButton):
    def __init__(self):
        ColourButton.__init__(self)
        self.index = None


    def set_current_marker(self):
        self.setText(u'\u2713')

    def clear_current_marker(self):
        self.setText('')

    def reset(self):
        self.setColour(self.initial_colour)
        self.setText('')

    def save(self):
        save_data={"colour":self.getColour()}
        return save_data

    def load(self, load_data, current_yarn):
        self.setColour(load_data["colour"])
        if self == current_yarn:
            self.set_current_marker()
        else:
            self.clear_current_marker()