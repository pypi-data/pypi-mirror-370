from tkinter import ttk

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.view import View

from app.components.clicker import Incrementer
from app.components.frame_swapper import FrameSwapper


class BelleView(View):
    def __init__(self, master):
        self.master = master
        self.title = 'belle'

    def set_view(self):
        belle = MainFrame(self.master, self.title)

        ttk.Label(belle, text = "c'est le belle").grid(row = 0)

        home_swapper = FrameSwapper(belle, 'vers home', 'home_view')
        home_swapper.frame.grid(row = 1, column = 0)

        coucou_swapper = FrameSwapper(belle, 'vers coucou', 'coucou_view')
        coucou_swapper.frame.grid(row = 1, column = 1)

        page_one_swapper = FrameSwapper(belle, 'to page one', 'page_one_view')
        page_one_swapper.frame.grid(row = 1, column = 0)

        belle.incrementer = Incrementer(belle, '1')
        belle.incrementer.frame.grid()
