#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'


from ColourButton import ColourButton
from YarnPalette import Yarn

class Loom():
    def __init__(self, max_warp_threads, pick_ct):
        self.warp_threads = []
        self.warp_thread_ct = 0
        self.max_warp_threads = max_warp_threads
        self.pick_ct = pick_ct

    def add_warp_thread(self):
        if self.warp_thread_ct < self.max_warp_threads:
            warp_thread = WarpThread(self.pick_ct)
            warp_thread.index = self.warp_thread_ct
            warp_thread.isHeddled = True if warp_thread.index % 2 == 0 else False
            self.warp_threads.append(warp_thread)
            self.set_alt_warp_thread()
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

    def set_alt_warp_thread(self):
        for warp_thread in self.warp_threads:
            alt_warp_thread_index = warp_thread.index + 1 if warp_thread.isHeddled else warp_thread.index - 1
            try:
                warp_thread.alt_warp_thread = self.warp_threads[alt_warp_thread_index]
            except IndexError:
                warp_thread.alt_warp_thread = None


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
            pick = Pick()
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