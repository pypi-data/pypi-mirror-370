"""Display About and History for a project."""
import tkinter as tk
from tkinter import ttk
from tkinterweb import HtmlFrame
from pathlib import Path
import markdown

from psiutils.constants import PAD, Pad
from psiutils.utilities import window_resize

from psiutils import text as txt

DEFAULT_GEOMETRY = '400x200'
HISTORY_GEOMETRY = '800x750'
HISTORY_FILE = 'HISTORY.md'
CSS = """
    body {color: black; font-size: 10px;}
    h1 {color: green; font-size: 20px;}
    h2 {color: green; font-size: 16px;}
    h3 {color: green; font-size: 15px;}
    p, ul, ol {color: black; font-size: 14px; font-weight: normal}
    """


class AboutFrame():
    def __init__(
            self,
            parent: tk.Frame,
            app_name: str,
            about_text: dict,
            parent_file: str,
            data_dir: str,
            ) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.about_text = about_text
        self.config = parent.config
        self.history_file = self._get_history_file(parent_file)
        self.data_dir = data_dir

        # tk variables
        self.app_name = tk.StringVar(value=app_name)

        style = ttk.Style()

        style.configure(
            'title.TLabel',
            font=('Helvetica', 12, 'bold'),
            )

        self.show()

    def show(self) -> None:
        root = self.root
        try:
            root.geometry(self.config.geometry[Path(__file__).stem])
        except KeyError:
            root.geometry(DEFAULT_GEOMETRY)
        root.title(f'About - {self.app_name.get()}')
        root.transient(self.parent.root)

        root.grab_set()

        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, __file__))

        root.bind('<Control-x>', self.dismiss)
        root.bind('<Control-h>', self._display_history)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)

        label = ttk.Label(
            frame, textvariable=self.app_name, style='title.TLabel')
        label.grid(row=0, column=0, columnspan=2,
                   sticky=tk.EW, padx=PAD, pady=PAD)

        text_frame = self._text_frame(frame)
        text_frame.grid(row=1, column=0, sticky=tk.EW)
        return frame

    def _text_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        for index, (title, about_text) in enumerate(self.about_text.items()):

            label = ttk.Label(frame, text=title.capitalize())
            label.grid(row=index, column=0, sticky=tk.E, padx=PAD, pady=PAD)

            label = ttk.Label(frame, text=about_text)
            label.grid(row=index, column=1, sticky=tk.W, padx=PAD, pady=PAD)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(1, weight=1)

        button = ttk.Button(
            frame, text='History', command=self._display_history, underline=0)
        button.grid(row=0, column=0, padx=Pad.W, sticky=tk.E)

        button = ttk.Button(
            frame, text=txt.EXIT, command=self.dismiss, underline=1)
        button.grid(row=0, column=1, padx=Pad.W, sticky=tk.E)

        return frame

    def _display_history(self, *args) -> None:
        if not self.history_file:
            return
        dlg = HistoryFrame(
            self, self.app_name.get(), self.history_file, self.data_dir)
        self.root.wait_window(dlg.root)

    def _get_history_file(self, parent_file: str) -> str | None:
        parent_dir = Path(parent_file).parent
        if Path(parent_dir, HISTORY_FILE).is_file():
            return Path(parent_dir, HISTORY_FILE)
        elif Path(parent_dir.parent, HISTORY_FILE).is_file():
            return Path(parent_dir.parent, HISTORY_FILE)
        return None

    def dismiss(self, *args) -> None:
        self.root.destroy()


class HistoryFrame():
    def __init__(
            self,
            parent: tk.Frame,
            app_name: str, history_path: Path,
            data_dir: str) -> None:
        self.root = tk.Toplevel(parent.root)
        self.parent = parent
        self.config = parent.config
        self.data_dir = data_dir

        # tk variables
        self.app_name = tk.StringVar(value=app_name)

        self.show()

        with open(history_path, 'r') as f_history:
            output = f_history.read()
        self.display_html(self.html_frame, output)

    def show(self) -> None:
        root = self.root
        try:
            root.geometry(self.config.geometry['history'])
        except KeyError:
            root.geometry(HISTORY_GEOMETRY)
        root.title(f'{self.app_name.get()} - History')
        root.transient(self.parent.root)

        # Make modal
        root.grab_set()

        root.bind('<Configure>',
                  lambda event, arg=None: window_resize(self, 'history'))

        root.bind('<Control-x>', self.dismiss)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        main_frame = self._main_frame(root)
        main_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=PAD, pady=PAD)
        self.button_frame = self._button_frame(root)
        self.button_frame.grid(row=8, column=0, columnspan=9,
                               sticky=tk.EW, padx=PAD, pady=PAD)

        sizegrip = ttk.Sizegrip(root)
        sizegrip.grid(sticky=tk.SE)

    def _main_frame(self, master: tk.Frame) -> ttk.Frame:
        frame = ttk.Frame(master)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.html_frame = HtmlFrame(
            frame, horizontal_scrollbar='auto', messages_enabled=False)
        self.html_frame.grid(row=0, column=0, sticky=tk.NSEW)

        return frame

    def _button_frame(self, master: tk.Frame) -> tk.Frame:
        frame = ttk.Frame(master)
        frame.columnconfigure(0, weight=1)

        button = ttk.Button(
            frame, text=txt.EXIT, command=self.dismiss, underline=1)
        button.grid(row=0, column=0, padx=Pad.W, sticky=tk.E)
        return frame

    def display_html(
            self, html_frame: HtmlFrame, text: str) -> None:
        html = markdown.markdown(text)
        page = f"""
            <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="utf-8">
                        <style>{CSS}</style>
                    </head>
                    <body>
                        <h1>{html}</h1>
                    </body>
                </html>"""
        self._write_html_file(html_frame, 'dummy.html', '')
        self._write_html_file(html_frame, 'temp.html', page)
        return page

    def _write_html_file(
            self, html_frame: HtmlFrame, file: str, text: str) -> None:
        temp_path = Path(self.data_dir, file)
        path = str(temp_path)
        with open(path, 'w') as f_html:
            f_html.write(text)
        html_frame.load_file(path)

    def dismiss(self, *args) -> None:
        self.root.destroy()
