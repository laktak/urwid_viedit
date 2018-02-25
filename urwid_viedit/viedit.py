import urwid

WS = [' ', '\t']

# tab completion from https://wiki.goffi.org/wiki/Urwid-satext/en

class ViEdit(urwid.Edit):
    """Edit widget supporting vi-mode and emacs keybindings."""

    yank_text = ""

    def __init__(self, *, completion_cb=None, normal_mode=True, **kwargs):
        """
        :param normal_mode: start in normal mode
        :param completion_cb:
            method that will be called for tab completion with 2 arguments:
            - the text to complete
            - if there was already a completion, a dict with
                - "completed": last completion
                - "completion_pos": cursor position where the completion starts
                - "position": last completion cursor position
            it should return the full text
        """

        super(ViEdit, self).__init__(**kwargs)
        self.normal = normal_mode
        self.op = None
        self.m = 1
        self.undo = [self.edit_text]
        self.undo_lvl = 0
        self.completion_cb = completion_cb
        self.completion_data = {}
        if self.normal: self.normal_key('$')

    def insert_yank(self, pos):
        text = ViEdit.yank_text
        self.set_edit_text(
            self.edit_text[:pos] +
            text +
            self.edit_text[pos:])
        self.set_edit_pos(pos + len(text))

    @staticmethod
    def get_text_sel(text, pos1, pos2):
        if pos2 < pos1: pos1, pos2 = pos2, pos1
        # return inside/outside
        return (text[pos1:pos2], text[:pos1] + text[pos2:])

    def tab_complete(self):
        if self.completion_cb == None: return
        try:
            before = self.edit_text[:self.edit_pos]
            if self.completion_data:
                if (not self.completion_data["completed"] or
                        self.completion_data["position"] != self.edit_pos or
                        not before.endswith(self.completion_data["completed"])):
                    self.completion_data.clear()
                else:
                    before = before[:-len(self.completion_data["completed"])]
            complete = self.completion_cb(before, self.completion_data)
            self.completion_data["completed"] = complete[len(before):]
            self.set_edit_text(complete + self.edit_text[self.edit_pos:])
            self.set_edit_pos(len(complete))
            self.completion_data["position"] = self.edit_pos
        except Exception:
            pass  # ignore

    def call_vi(self, key, op=None):
        self.normal = True
        self.op = op
        self.normal_key(key)
        self.normal = False

    def normal_key(self, key):
        pos = self.edit_pos
        text = self.edit_text
        tlen = len(text)
        last = tlen - 1

        if pos >= len(self.edit_text):
            pos = len(self.edit_text) - 1
            self.set_edit_pos(pos)

        if self.undo[self.undo_lvl] != text:
            self.undo_lvl = len(self.undo)
            self.undo = self.undo[:self.undo_lvl] + [text]

        def get_b(pos):
            while text[pos - 1] in WS and pos > 0: pos -= 1
            while not text[pos - 1] in WS and pos > 0: pos -= 1
            return pos

        def get_w(pos):
            while not text[pos] in WS and pos < last: pos += 1
            while text[pos] in WS and pos < last: pos += 1
            return pos

        def get_e(pos):
            while text[pos + 1] in WS and pos + 1 < last: pos += 1
            while not text[pos + 1] in WS and pos + 1 < last: pos += 1
            return pos

        if self.op in ['c', 'd', 'y']:
            pos2 = pos
            stext = None
            if key in ['w', 'W']:
                for i in range(self.m): pos2 = get_w(pos2)
                stext = ViEdit.get_text_sel(text, pos, pos2)
            elif key in ['b', 'B']:
                for i in range(self.m): pos2 = get_b(pos2)
                stext = ViEdit.get_text_sel(text, pos2, pos)
                self.set_edit_pos(pos2)
            elif key == '0':
                stext = ViEdit.get_text_sel(text, 0, pos)
                self.set_edit_pos(0)
            elif key == '$':
                stext = ViEdit.get_text_sel(text, pos, tlen)

            if stext:
                ViEdit.yank_text = stext[0]
                if self.op in ['c', 'd']: self.set_edit_text(stext[1])

            if self.op == 'c': self.normal = False
            self.op = None
            return

        if key == 'i':
            self.normal = False
        elif key == 'I':
            self.call_vi('0')
        elif key == 'a':
            self.set_edit_pos(pos + 1)
            self.normal = False
        elif key == 'A':
            self.call_vi('$')
            self.call_vi('a')
        elif key == 'C':
            self.call_vi('$', 'c')
        elif key == 'h':
            self.set_edit_pos(pos - self.m)
        elif key == 'l':
            if pos < last: self.set_edit_pos(pos + self.m)
        elif key == '0':
            self.set_edit_pos(0)
        elif key == '$':
            self.set_edit_pos(last)
        elif key == 'x':
            if pos == last: pos -= 1
            for i in range(self.m):
                text = ViEdit.get_text_sel(text, pos, pos + 1)[1]
            self.set_edit_text(text)
            self.set_edit_pos(pos)
        elif key == 'P':
            self.insert_yank(self.edit_pos)
        elif key == 'p':
            self.insert_yank(self.edit_pos - 1)
        elif key in ['w', 'W']:
            for i in range(self.m): pos = get_w(pos)
            self.set_edit_pos(pos)
        elif key in ['b', 'B']:
            for i in range(self.m): pos = get_b(pos)
            self.set_edit_pos(pos)
        elif key in ['e', 'E']:
            for i in range(self.m): pos = get_e(pos)
            self.set_edit_pos(pos)
        elif key == 'u':
            if self.undo_lvl > 0:
                self.undo_lvl -= 1
                tx = self.undo[self.undo_lvl]
                self.set_edit_text(tx)
        elif key == 'ctrl r':
            if self.undo_lvl < len(self.undo) - 1:
                self.undo_lvl += 1
                tx = self.undo[self.undo_lvl]
                self.set_edit_text(tx)
        # TODO
        # elif key == '.':
        elif key in ['c', 'd', 'y']:
            self.op = key
            return
        elif key in [str(c) for c in range(1, 10)]:
            self.m = int(key)
            return

        self.m = 1

    def insert_key(self, key):
        if key == "esc":
            self.set_edit_pos(self.edit_pos - 1)
            self.normal = True
            self.op = None

        # emacs like
        elif key == "ctrl a":
            self.call_vi('0')
        elif key == "ctrl e":
            self.call_vi('$')
        elif key == "ctrl u":
            self.call_vi('0', 'd')
        elif key == "ctrl k":
            self.call_vi('$', 'd')
        elif key == "ctrl y":
            self.call_vi('P')
        elif key == "ctrl w":
            self.call_vi('b', 'd')
        elif key == "ctrl b":
            self.call_vi('b')
        elif key == "ctrl f":
            self.call_vi('w')
        elif key == "tab":
            self.tab_complete()
        else: return key

    def keypress(self, size, key):
        key = self.normal_key(key) if self.normal else self.insert_key(key)
        if key is not None:
            return super(ViEdit, self).keypress(size, key)
