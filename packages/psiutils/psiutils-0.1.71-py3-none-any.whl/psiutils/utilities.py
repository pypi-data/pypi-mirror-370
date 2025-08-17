"""Common methods for psiutils."""
from pathlib import Path
import tkinter as tk
import ctypes
from typing import Any
import platform

from psiconfig import TomlConfig
from psiutils._logger import logger
import psiutils.text as txt

DEFAULT_GEOMETRY = '500x400'


def display_icon(root: tk.Tk, icon_file_path: str,
                 ignore_error: bool = True) -> None:
    if platform.system() == 'Windows':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('_')
    try:
        icon = tk.PhotoImage(master=root, file=icon_file_path)
        root.wm_iconphoto(True, icon)
    except tk.TclError as err:
        if ignore_error and txt.NO_SUCH_FILE in str(err):
            return
        print(f'Cannot find icon file: {icon_file_path}')


class Enum():
    def __init__(self, values: dict) -> None:
        self.values = invert(values)


def confirm_delete(parent: Any) -> str:
    question = txt.DELETE_THESE_ITEMS
    return tk.messagebox.askquestion(
        'Delete items', question, icon='warning', parent=parent)


def create_directories(path: str | Path) -> bool:
    """Create directories recursively."""
    print('*** psiutils  "create_directories" called: DEPRECATED ***')
    print('Use Path(path).mkdir(parents=True, exist_ok=True) instead!!!')
    create_parts = []
    create_path = Path(path)
    for part in create_path.parts:
        create_parts.append(part)
        new_path = Path(*create_parts)
        if not Path(new_path).is_dir():
            try:
                Path(new_path).mkdir()
            except PermissionError:
                print(f'Invalid file path: {new_path}')
                return False
    return True


def invert(enum: dict) -> dict:
    """Add the inverse items to a dictionary."""
    output = {}
    for key, item in enum.items():
        output[key] = item
        output[item] = key
    return output


def enable_frame(parent: tk.Frame, enable: bool = True) -> None:
    state = tk.NORMAL if enable else tk.DISABLED
    for child in parent.winfo_children():
        w_type = child.winfo_class()
        if w_type in ('Frame', 'Labelframe', 'TFrame', 'TLabelframe'):
            enable_frame(child, enable)
        else:
            child.configure(state=state)


# def geometry(geometry: dict, form: str = '') -> str:
#     system = platform.system()
#     if system not in ['Linux', 'Windows']:
#         system = 'Linux'
#     return geometry[Path(form).stem][system]

def geometry(config: TomlConfig, file: Path, default: str = '') -> str:
    if not default:
        default = DEFAULT_GEOMETRY
    try:
        return config.geometry[Path(file).stem]
    except KeyError:
        return default


def window_resize(master: tk.Tk, file: str, *args) -> None:
    match = master.root.geometry().split('+')
    window_geometry = (
        f'{master.root.winfo_width()}x{master.root.winfo_height()}+'
        f'{master.root.winfo_x()}+{match[2]}')
    master.config.read()
    geometry = master.config.geometry
    geometry[Path(file).stem] = window_geometry
    master.config.update('geometry', geometry)
    master.config.save()
