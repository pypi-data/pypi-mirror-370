"""Various Tkinter widgets and methods."""
import tkinter as tk
from tkinter import ttk
import contextlib


from .constants import PAD, COLOURS
from ._about_frame import AboutFrame

HAND = 'hand2'
DIM_TEXT = '#555'


class About(AboutFrame):
    def __init__(self, parent, app_name, about_text, parent_file, data_dir):
        super().__init__(parent, app_name, about_text, parent_file, data_dir)
        pass


class PsiText(tk.Text):
    def __init__(self, *args, **kwargs):
        """A text widget that reports on internal widget commands."""
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = f"{self._w}_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result


def get_styles() -> ttk.Style:
    style = ttk.Style()
    # Labels - foreground
    style.configure('red-fg.TLabel', foreground='red')
    style.configure('green-fg.TLabel', foreground='green')
    style.configure('blue-fg.TLabel', foreground='blue')
    style.configure('yellow-fg.TLabel', foreground='yellow')
    style.configure('grey-fg.TLabel', foreground='grey')
    style.configure('orange-fg.TLabel', foreground='orange')

    # Labels - background
    style.configure('red-bg.TLabel', background='red')
    style.configure('green-bg.TLabel', background='green')
    style.configure('blue-bg.TLabel', background='blue')
    style.configure('yellow-bg.TLabel', background='yellow')
    style.configure('grey-bg.TLabel', background='grey')
    style.configure('orange-bg.TLabel', background='orange')

    # Entries - background
    style.configure('grey-bg.TEntry', fieldbackground='grey')
    style.configure(
        'pale-grey-bg.TEntry', fieldbackground=COLOURS['pale-grey'])

    style.configure('red-bg.TEntry', fieldbackground='red')
    style.configure('green-bg.TEntry', fieldbackground='green')
    style.configure('orange-bg.TEntry', fieldbackground='orange')
    style.configure(
        'pale-umber-bg.TEntry', fieldbackground=COLOURS['pale-umber'])
    style.configure(
        'pale-red-bg.TEntry', fieldbackground=COLOURS['pale-red'])

    # Entries - foreground
    style.configure('red-fg.TEntry', foreground='red')
    style.configure('green-fg.TEntry', foreground='green')
    style.configure('orange-fg.TEntry', foreground='orange')

    # Frames
    style.configure('red.TFrame', background='red')
    style.configure('green.TFrame', background='green')
    style.configure('blue.TFrame', background='blue')
    style.configure('yellow.TFrame', background='yellow')
    style.configure('grey.TFrame', background='grey ')

    # radiobuttons
    style.configure('red-fg.TRadiobutton', foreground='red')
    style.configure('green-fg.TRadiobutton', foreground='green')

    # Tree view
    style.map('Treeview',
              foreground=fixed_map(style, 'foreground'),
              background=fixed_map(style, 'background'))

    # Emoji font
    style.configure('Emoji.TButton', font=('Segoe UI Emoji', 8))

    return style


def fixed_map(style, option):
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out

    # style.map() returns an empty list for missing options, so this should
    # be future-safe
    return [elm for elm in style.map('Treeview', query_opt=option)
            if elm[:2] != ('!disabled', '!selected')]


def vertical_scroll_bar(
        master: tk.Frame,
        widget: tk.Widget,
        ) -> ttk.Scrollbar:

    v_scroll = ttk.Scrollbar(
        master,
        orient='vertical',
        command=widget.yview
        )
    widget.configure(yscrollcommand=v_scroll.set)
    widget['yscrollcommand'] = v_scroll.set
    return v_scroll


def enter_widget(event: object = None) -> None:
    if tk.DISABLED in event.widget.state():
        return
    event.widget.winfo_toplevel().config(cursor=HAND)


def _leave_widget(event: object = None) -> None:
    event.widget.winfo_toplevel().config(cursor='')


def clickable_widget(widget: object) -> None:
    widget.bind('<Enter>', enter_widget)
    widget.bind('<Leave>', _leave_widget)


def status_bar(master: tk.Frame, textvariable: tk.StringVar,
               colour: str = DIM_TEXT) -> tk.Frame:
    frame = ttk.Frame(master, relief=tk.SUNKEN)
    frame.columnconfigure(1, weight=1)
    label = tk.Label(frame, fg=colour, textvariable=textvariable)
    label.grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=1)
    return frame


@contextlib.contextmanager
def WaitCursor(root):
    root.config(cursor='watch')
    root.update()
    try:
        yield root
    finally:
        root.config(cursor='')


@contextlib.contextmanager
def MoveCursor(root):
    root.config(cursor='fleur')
    root.update()
    try:
        yield root
    finally:
        root.config(cursor='')


def separator_frame(master: tk.Frame, text: str) -> tk.Frame:
    frame = ttk.Frame(master)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(2, weight=1)

    separator = ttk.Separator(frame, orient='horizontal')
    separator.grid(row=0, column=0, sticky=tk.EW, padx=PAD, pady=PAD*4)

    label = ttk.Label(frame, text=text)
    label.grid(row=0, column=1, sticky=tk.E)

    separator = ttk.Separator(frame, orient='horizontal')
    separator.grid(row=0, column=2, sticky=tk.EW, padx=PAD)
    return frame


class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.canvas = tk.Canvas(
            self,
            bd=0,
            width=200, height=300,
            yscrollcommand=vscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.config(command=self.canvas.yview)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = ttk.Frame(self.canvas)
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior_id = self.canvas.create_window(
            0, 0, window=self.interior, anchor=tk.NW)

    def _configure_interior(self, event):
        # Update the scroll bars to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(),
                self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame.
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas.
            self.canvas.itemconfigure(
                self.interior_id, width=self.canvas.winfo_width())


class Tooltip:
    def __init__(self, widget,
                 *,
                 bg='#FFFFEA',
                 pad=(5, 3, 5, 3),
                 text='',
                 textvariable=None,
                 wait_time=400,
                 wrap_length=250,
                 vertical_offset=0,):
        self.wait_time = wait_time  # in milliseconds
        self.wrap_length = wrap_length  # in pixels
        self.vertical_offset = vertical_offset
        self.widget = widget
        self.text = text
        self.textvariable = textvariable
        self.widget.bind('<Enter>', self.onEnter)
        self.widget.bind('<Leave>', self.onLeave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def __repr__(self) -> str:
        return f'Tooltip: {self.textvariable.get()}'

    def onEnter(self, *args):
        if not self.text:
            if not self.textvariable:
                return
            if not self.textvariable.get():
                return
        # Ensure text gets cleared in case the textvariable is empty
        self.text = ''
        if self.textvariable.get():
            self.text = self.textvariable.get()
        self.schedule()

    def onLeave(self, *args):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        if not self.text:
            return

        def tip_pos_calculator(widget, label,
                               *,
                               tip_delta=(10, 5), pad=(5, 3, 5, 3)):

            w = widget

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

            width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                             pad[1] + label.winfo_reqheight() + pad[3])

            mouse_x, mouse_y = w.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:

                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                y1 = 0

            return x1, y1

        bg = self.bg
        widget = self.widget

        # creates a toplevel window
        self.tw = tk.Toplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = tk.Frame(self.tw,
                       background=bg,
                       borderwidth=0)
        label = tk.Label(win,
                         text=self.text,
                         justify=tk.LEFT,
                         background=bg,
                         relief=tk.GROOVE,
                         borderwidth=3,
                         wraplength=self.wrap_length)

        label.grid(sticky=tk.NSEW)
        win.grid()

        x, y = tip_pos_calculator(widget, label)

        self.tw.wm_geometry("+%d+%d" % (x, y+self.vertical_offset))
        # self.tw.wm_geometry(f'{x}x{y}')

    def hide(self):
        if tw := self.tw:
            tw.destroy()
        self.tw = None
