# psiutils

Various utility classes and methods, mainly, but not exclusively Tkinter.

## Installation

```bash
pip install psiutils
```

## Main functionality

### Buttons

A classes and methods to organise the display and enabling of Tkinter buttons

### Constants

The module exposes certain constants particularly useful with Tkinter dialogs

e.g YES  (True), NO (False), CANCEL (None)

and Modes e.g. VIEW, NEW, EDIT, DELETE

### Drag manager

A drag and drop implementation for tkinter trees (see module documentation)

### Icecream

Set up icecream for an application.

### Known paths

Various path utilities including: return to path to a Windows known folder.

### Menus

A classes and methods to organise the display and enabling of Tkinter Menus


### Treeview

A classes and methods to organise the display  of Tkinter treeviews including sort and treeview with checkboxes.

### Utilities

Various utility classes and functions including:

* display_icon
* create_directories

    should really use (pathlib.Path('\<dir>').mkdir(parents=True, exist_ok=True))

### Widgets

Various widgets and utilities including:

* PsiText a Tkinter text widget that detects changes
* vertical_scroll_bar
* clickable_widget (change cursor when entered)
* status_bar
* WaitCursor
* separator_frame
* VerticalScrolledFrame
* Tooltip
* AboutFrame (provide labels and text in a dict)
