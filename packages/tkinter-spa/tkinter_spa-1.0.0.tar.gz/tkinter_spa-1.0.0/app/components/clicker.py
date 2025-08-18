import tkinter as tk

from tkinter import ttk


class Incrementer():
    def __init__(self, parent, widget_name):
        self.parent = parent
        self.name = f'incrementer_{widget_name}'
        self.counter = tk.IntVar()
        self.frame = self.set_component()

    def set_component(self):
        frame = ttk.Frame(self.parent, name = self.name)
        ttk.Label(frame, textvariable = self.counter).grid(column = 0, row = 1)
        ttk.Button(
            frame, name = 'bouton', text = 'Cliquez', cursor = 'hand2',
            command = self.increment
        ).grid(column = 1, row = 1)

        return frame

    def increment(self):
        self.counter.set(self.counter.get() + 1)
