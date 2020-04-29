from ColourButton import ColourButton, PickButton


def dump_func_name(func):
    def echo_func(*func_args, **func_kwargs):
        print('')
        print('Start func: {}'.format(func.__name__))
        return func(*func_args, **func_kwargs)

    return echo_func


class Loom():
    def __init__(self, max_warp_threads, pick_ct, initial_warp_size):
        self.warp_threads = []
        self.warp_thread_ct = 0
        self.max_warp_threads = max_warp_threads
        self.pick_ct = pick_ct
        self.is_modified = False
        self.create_initial_warp(initial_warp_size)

    def create_initial_warp(self, warp_size):
        for _ in range(warp_size):
            self.add_warp_thread()

    def add_warp_thread(self):
        if self.warp_thread_ct < self.max_warp_threads:
            warp_thread = self.WarpThread(self.pick_ct)
            warp_thread.index = self.warp_thread_ct
            warp_thread.set_heddled()
            self.warp_threads.append(warp_thread)
            self.set_pickup_thread(warp_thread)
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
            # warp.deleteLater()
            del warp_thread
            del self.warp_threads[-1]
            prev_thread = self.warp_threads[self.warp_thread_ct - 1]
            if prev_thread.isHeddled:
                self.clear_pickup_thread(prev_thread)

    def set_pickup_thread(self, warp_thread):
        pickup_warp_index = warp_thread.index + 1 if warp_thread.isHeddled else warp_thread.index - 1
        try:
            pickup_thread = self.warp_threads[pickup_warp_index]
            warp_thread.pickup_warp = pickup_thread
            pickup_thread.pickup_warp = warp_thread
        except IndexError:
            self.clear_pickup_thread(warp_thread)

    def clear_pickup_thread(self, warp_thread):
        warp_thread.pickup_warp = None
        for pick in warp_thread.picks:
            pick.isPicked = False
            pick.clear_pickup_text()
            pick.set_display_colour(warp_thread, None)

    def change_warp_yarn(self, yarn):
        for warp_thread in self.warp_threads:
            if warp_thread.yarn_index == yarn.index:
                warp_thread.change_yarn(yarn)
        self.is_modified = True

    def reset(self, initial_warp_size):
        self.is_modified = False
        self.warp_thread_ct=initial_warp_size
        for warp_thread in self.warp_threads:
            warp_thread.reset()


    def save(self):
        save_data = {"warp_thread_ct": self.warp_thread_ct}
        save_data["is_modified"] = self.is_modified
        save_warps = [warp_thread.save() for warp_thread in self.warp_threads]
        save_data["warp_threads"] = save_warps
        return save_data

    def load(self, load_data):
        # for warp, warp_data in zip(self.warp_threads, load_data["warp_threads"]):
        #     warp.load(warp_data)
        #     self.set_pickup_thread(warp)
        #     for pick, pick_data in zip(warp.picks, warp_data["pick_data"]):
        #         pick.load(pick_data)
        #         pick.set_display_colour(warp, warp.pickup_warp)
        #         pick.set_pickup_text(warp)
        # self.is_modified = load_data["is_modified"]


        # for warp, warp_data in zip(self.warp_threads, load_data["warp_threads"]):
        #     warp.load(warp_data)
        #     self.set_pickup_thread(warp)
        # for warp in self.warp_threads:
        #     for pick, pick_data in zip(warp.picks, warp_data["pick_data"]):
        #         pick.load(pick_data)
        #         pick.set_display_colour(warp, warp.pickup_warp)
        #         #pick.set_pickup_text(warp)
        # self.is_modified = load_data["is_modified"]

        for warp, warp_data in zip(self.warp_threads, load_data["warp_threads"]):
            warp.load(warp_data)
            for pick, pick_data in zip(warp.picks, warp_data["pick_data"]):
                pick.load(pick_data)
        for warp in self.warp_threads:
            self.set_pickup_thread(warp)
            for pick in warp.picks:
                pick.set_display_colour(warp, warp.pickup_warp)
                pick.set_pickup_text(warp)
        self.is_modified = load_data["is_modified"]


    #### Warp Thread ####
    class WarpThread(ColourButton):
        def __init__(self, pick_ct):
            ColourButton.__init__(self)
            self.index = None
            self.yarn_index = None
            self.pickup_warp = None
            self.isHeddled = True
            self.picks = []
            for pick_no in range(pick_ct):
                pick = self.Pick()
                pick.index = pick_no
                self.picks.append(pick)

        def set_heddled(self):
            self.isHeddled = True if self.index % 2 == 0 else False

        def change_yarn(self, yarn):
            self.new_warp_colour(yarn)
            self.new_pick_colour()
            try:
                self.pickup_warp.new_pick_colour()
            except AttributeError:
                pass

        def new_warp_colour(self, yarn):
            self.yarn_index = yarn.index
            self.setColour(yarn.getColour())

        def new_pick_colour(self):
            for pick in self.picks:
                pick.set_display_colour(self, self.pickup_warp)

        def toggle_pick(self, pick_index):
            self.picks[pick_index].do_toggle(self, self.pickup_warp)

        def reset(self):
            self.setColour(self.initial_colour)
            self.yarn_index = None
            for pick in self.picks:
                pick.reset()

        def save(self):
            save_data = {"index": self.index, "colour": self.getColour(), "yarn_index": self.yarn_index}
            pick_data = [pick.save() for pick in self.picks]
            save_data["pick_data"] = pick_data
            return save_data

        def load(self, load_data):
            self.index = load_data["index"]
            self.colour = load_data["colour"]
            self.setColour(self.colour)
            self.yarn_index = load_data["yarn_index"]
            self.set_heddled()

        #### Pick ####
        class Pick(PickButton):
            def __init__(self):
                PickButton.__init__(self)
                self.index = None
                self.isPicked = False

            def do_toggle(self, warp_thread, alt_warp_thread):
                if alt_warp_thread:
                    self.isPicked = not self.isPicked
                    self.set_display_colour(warp_thread, alt_warp_thread)
                    self.set_pickup_text(warp_thread);

            def set_display_colour(self, warp_thread, pickup_thread):
                if not self.isPicked:
                    self.setColour(warp_thread.getColour())
                else:
                    try:
                        self.setColour(pickup_thread.getColour())
                    except AttributeError:
                        self.setColour(warp_thread.getColour())

            def set_pickup_text(self, warp_thread):
                if self.isPicked:
                    s = u'\u2BC6' if warp_thread.isHeddled else (u'\u2BC5')
                    self.setText(s)
                else:
                    self.clear_pickup_text()

            def clear_pickup_text(self):
                self.setText('')

            def reset(self):
                self.setColour(self.initial_colour)
                self.isPicked = False
                self.clear_pickup_text()

            def save(self):
                save_data = {"isPicked": self.isPicked}
                return save_data

            def load(self, load_data):
                self.isPicked = load_data["isPicked"]
