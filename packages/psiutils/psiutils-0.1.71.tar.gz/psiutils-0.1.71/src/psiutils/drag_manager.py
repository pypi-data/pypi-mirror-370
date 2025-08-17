"""
    A drag and drop implementation for tkinter trees

    Usage:

    def _setup_drag_and_drop(self):
        self.player_tuples = []
        for index in range(len(self.pair_labels)):
            if index <= len(self.player_1) - 1:
                self.player_tuples.append(
                    (self.player_1_widgets[index], self.player_1[index])
                    )
                self.player_tuples.append(
                    (self.player_2_widgets[index], self.player_2[index])
                    )
            dnd = DragManager(self)
        dnd.add_draggable(self.tree, self.player_tuples)
"""


import tkinter as tk

DRAG_TOKEN_X_OFFSET = 11
DRAG_TOKEN_Y_OFFSET = 12
DRAG_TOKEN_TEXT = '... ...'


class DragManager():
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.root
        self.values = []
        self.source_widget = None
        self.target_widgets = []
        self.drop_widget = None
        self.drag_token = tk.Label(self.root, text=DRAG_TOKEN_TEXT, bg='white',
                                   borderwidth=2, relief='groove')

    def add_draggable(self, source_widget, target_widgets: list[tuple]):
        """
            source_widget is the tree from which we will be selecting an item
            target_widgets is a list of tuples. One tuple per target; the
                first entry being the widget, the second its text_variable
            drag_token is a label widget that moves with the hand cursor to
                indicate dragging in progress
        """
        source_widget.bind("<ButtonPress-1>", self.on_start)
        source_widget.bind("<B1-Motion>", self.on_drag)
        source_widget.bind("<ButtonRelease-1>", self.on_drop)
        source_widget.configure(cursor="hand1")
        self.source_widget = source_widget
        self.target_widgets = target_widgets

    def _get_source_coords(self) -> tuple:
        sx = self.source_widget.winfo_rootx()
        sy = self.source_widget.winfo_rooty()
        return (sx, sy)

    def _place_token(self, widget):
        sx = self.parent.main_frame.winfo_rootx()
        sy = self.parent.main_frame.winfo_rooty()
        x, y = widget.winfo_pointerxy()
        self.drag_token.place(x=x-sx-DRAG_TOKEN_X_OFFSET,
                              y=y-sy-DRAG_TOKEN_Y_OFFSET)

    def on_start(self, event):
        widget = event.widget
        selected_item = widget.identify_row(event.y)
        if not selected_item:
            return
        self.values = widget.item(selected_item)['values']

        self._place_token(widget)

    def on_drag(self, event):
        self._place_token(event.widget)

    def on_drop(self, event):
        self.drag_token.place_forget()

        x, y = event.widget.winfo_pointerxy()
        for target_widget in self.target_widgets:
            target = target_widget[0]
            x_coords = (target.winfo_rootx(),
                        target.winfo_rootx() + target.winfo_width())
            y_coords = (target.winfo_rooty(),
                        target.winfo_rooty() + target.winfo_height())

            if (x >= x_coords[0] and x <= x_coords[1] and
                    y >= y_coords[0] and y <= y_coords[1]):
                name = f'{self.values[0]} {self.values[1]} {self.values[2]}'
                # Set the widget's textvariable to the selected value
                self.drop_widget = target_widget[0]
                target_widget[1].set(name.strip())
                break
