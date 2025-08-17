"""Tkinter based error messages."""
import tkinter as tk
from tkinter import messagebox

ERROR = 'Error'
NO_MESSAGE = 'No message defined for error.'


class ErrorMsg():
    def __init__(self, *args, **kwargs) -> None:
        self.header: str = ERROR
        self.message: str = NO_MESSAGE

        if 'header' in kwargs:
            self.header = kwargs['header']

        if 'message' in kwargs:
            self.message = kwargs['message']

    def show_message(self, root: tk.Tk) -> str:
        messagebox.showerror(self.header, self.message, parent=root)
