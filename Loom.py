#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'brian'

from ColourButton import ColourButton

class Loom():
    def __init__(self, max_warp_threads, pick_ct):
        self.warp_threads = []
        self.warp_thread_ct = 0
        self.max_warp_threads = max_warp_threads
        self.pick_ct = pick_ct
        self.is_modified = False
        self.initial_warp_ct = 12
        self.create_initial_warp()

    def create_initial_warp(self):
        for _ in range(self.initial_warp_ct):
            self.add_warp_thread()

    def add_warp_thread(self):
        if self.warp_thread_ct < self.max_warp_threads:
            warp_thread = self.WarpThread(self.pick_ct)
            warp_thread.index = self.warp_thread_ct
            warp_thread.isHeddled = True if warp_thread.index % 2 == 0 else False
            self.warp_threads.append(warp_thread)
            self.set_alt_warp_threads()
            self.warp_thread_ct += 1
            return warp_thread
        else:
            return None

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
            del self.warp_threads[-1]


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
        self.is_modified = True

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
                        print("Error")
                        self.setColour(warp_thread.getColour())

            def toggle_pick(self, warp_thread, alt_warp_thread):
                self.isPicked = not self.isPicked
                self.set_display_colour(warp_thread, alt_warp_thread)

            def reinitialise(self):
                self.setColour(self.inital_colour)
                self.isPicked = False

            def reload(self, load_data):
                self.isPicked = load_data["isPicked"]
