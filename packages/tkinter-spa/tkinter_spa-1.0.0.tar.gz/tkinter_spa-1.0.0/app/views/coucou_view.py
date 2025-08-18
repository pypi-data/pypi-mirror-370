from tkinter import Listbox, StringVar, ttk

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.view import View

from app.components.frame_swapper import FrameSwapper

class CoucouView(View):
    def __init__(self, master):
        self.master = master
        self.title = 'coucou'
        self.entry_text = StringVar()
        self.listvar = []
        self.lbox = StringVar(value = self.listvar)

    def set_view(self):
        coucou = MainFrame(self.master, self.title)

        ttk.Label(coucou, text = "c'est le coucou").grid(row = 0)

        home_swapper = FrameSwapper(coucou, 'vers home', 'home_view')
        home_swapper.frame.grid(row = 1, column = 0)

        belle_swapper = FrameSwapper(coucou, 'vers belle', 'belle_view')
        belle_swapper.frame.grid(row = 1, column = 1)

        ttk.Label(coucou, text = 'Liste').grid(row = 2, column = 0)
        Listbox(coucou, listvariable = self.lbox, height = 10).grid(row = 3, column = 0)
        entry = ttk.Entry(coucou, textvariable = self.entry_text)
        entry.grid(row = 4, column = 0)
        ttk.Button(
            coucou, text = 'Ajoutez à la liste', cursor = 'hand2',
            command = lambda: self.add_entry_to_list(entry)
        ).grid(column = 1, row = 4)

    def add_entry_to_list(self, widget):
        self.listvar.append(self.entry_text.get())
        self.lbox.set(self.listvar)
        self.entry_text.set('')
        widget.focus()
