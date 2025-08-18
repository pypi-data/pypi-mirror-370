import tkinter as tk

from tkinter import ttk

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.view import View
from tkinter_spa.tk_root import set_geometry

from app.components.clicker import Incrementer
from app.components.frame_swapper import FrameSwapper


class HomeView(View):
    def __init__(self, master):
        self.master = master
        self.title = 'home'

    def set_view(self):
        home = MainFrame(self.master, self.title)

        ttk.Label(home, text = "c'est le home").grid(row = 0)

        coucou_swapper = FrameSwapper(home, 'vers coucou', 'coucou_view')
        coucou_swapper.frame.grid(row = 1, column = 0)

        belle_swapper = FrameSwapper(home, 'vers belle', 'belle_view')
        belle_swapper.frame.grid(row = 1, column = 1)

        ttk.Button(
            home, text = 'vers détail', cursor = 'hand2',
            command = self.open_detail
        ).grid(row = 1, column = 2)

        home.incrementer = Incrementer(home, '1')
        home.incrementer.frame.grid(pady = 80)

    def open_detail(self):
        window = tk.Toplevel(name = 'home_detail')
        window.title('détail')
        window.geometry(set_geometry(self.master, 300, 50))

        frame = ttk.Frame(window)
        ttk.Label(frame, text = "c'est le détail de home").grid(pady = 10)
        frame.pack()
