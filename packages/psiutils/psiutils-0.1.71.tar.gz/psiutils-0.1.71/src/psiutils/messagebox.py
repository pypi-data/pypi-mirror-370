"""Custom tkinter messagebox."""
import tkinter as tk
from tkinter import ttk
from tkinter import font
from pathlib import Path
from PIL import ImageTk, Image

from psiutils.constants import PAD

import psiutils.text as text

icons = {
    'info': 'icon-info.png',
    'error': 'icon-error.png',
    'query': 'icon-query.png',
}

icon_text = {
    'info': 'Info:',
    'error': 'Error!!!',
    'query': 'Query!!!',
}

STATUS = {
    'yes': True,
    'no': False,
    'cancel': None,
}


class MessageBox():
    def __init__(
            self,
            title: str = '',
            message: str = '',
            parent: tk.Tk = None,
            icon: str = 'info',
            buttons: list[str] = None,
            ) -> None:
        self.parent = parent
        self.root = tk.Toplevel(parent.root)
        self.title = title
        self.icon = icon
        if not buttons:
            buttons = ['ok']
        self.buttons = buttons
        self.status = None

        # tk variables
        self.message_text = tk.StringVar(value=message)

        self.show()

    def show(self) -> None:
        root = self.root
        root.transient(self.parent.root)
        root.title(self.title)

        root.bind('<Control-o>', self._dismiss)

        if isinstance(self.icon, str):
            path = Path(Path(__file__).parent, 'images', icons[self.icon])
            try:
                self.icon_image = ImageTk.PhotoImage(Image.open(path))
            except FileNotFoundError:
                pass
        else:
            self.icon_image = self.icon

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        try:
            label = tk.Label(frame, image=self.icon_image)
        except AttributeError:
            label = tk.Label(
                frame, text=icon_text[self.icon],
                font=(font.nametofont('TkDefaultFont'), 12, 'bold'))
        label.grid(row=0, column=0)

        label = ttk.Label(
            frame,
            textvariable=self.message_text,
            font=(font.nametofont('TkDefaultFont'), 12, 'bold')
            )
        label.grid(row=0, column=1, sticky=tk.NSEW, padx=PAD, pady=PAD)

        button_frame = self._button_frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2,
                          padx=PAD, pady=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)

        buttons = self._get_buttons(frame)
        for index, button_name in enumerate(self.buttons):
            button = buttons[button_name]
            button.grid(row=0, column=index, padx=PAD)
        return frame

    def _get_buttons(self, frame: ttk.Frame) -> dict[str, ttk.Button]:
        return {
            'ok': ttk.Button(
                frame, text=text.OK, command=self._ok, underline=0),
            'yes': ttk.Button(
                frame, text=text.YES, command=self._yes, underline=0),
            'no': ttk.Button(
                frame, text=text.NO, command=self._no, underline=0),
            'cancel': ttk.Button(
                frame, text=text.CANCEL, command=self._cancel, underline=0),
        }

    def _ok(self, *args) -> None:
        self.status = STATUS['cancel']
        self._dismiss()

    def _yes(self, *args) -> None:
        self.status = STATUS['yes']
        self._dismiss()

    def _no(self, *args) -> None:
        self.status = STATUS['no']
        self._dismiss()

    def _cancel(self, *args) -> None:
        self.status = STATUS['cancel']
        self._dismiss()

    def _dismiss(self, *args) -> None:
        self.root.destroy()


def showinfo(
        parent: tk.Tk = None,
        title: str = '',
        message: str = '',
        ) -> None:

    messagebox = MessageBox(
        title=title,
        message=message,
        parent=parent,
        icon='info',
        )

    parent.root.wait_window(messagebox.root)
    return messagebox.status


def showerror(
        parent: tk.Tk = None,
        title: str = '',
        message: str = '',
        ) -> None:

    messagebox = MessageBox(
        title=title,
        message=message,
        parent=parent,
        icon='error',
        )

    parent.root.wait_window(messagebox.root)
    return messagebox.status


def askyesno(
        parent: tk.Tk = None,
        title: str = '',
        message: str = '',
        ) -> None | bool:

    messagebox = MessageBox(
        title=title,
        message=message,
        parent=parent,
        icon='query',
        buttons=['yes', 'no']
        )

    parent.root.wait_window(messagebox.root)
    return messagebox.status
