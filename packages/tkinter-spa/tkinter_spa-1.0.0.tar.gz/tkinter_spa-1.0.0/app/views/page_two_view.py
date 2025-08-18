from tkinter import ttk

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.view import View

from app.components.clicker import Incrementer
from app.components.frame_swapper import FrameSwapper

class PageTwoView(View):
    def __init__(self, master):
        self.master = master
        self.title = 'Page two'

    def set_view(self):
        page_two = MainFrame(self.master, self.title)

        ttk.Label(page_two, text = "This the page two").grid(row = 0)

        page_one_swapper = FrameSwapper(page_two, 'to page one', 'page_one_view')
        page_one_swapper.frame.grid(row = 1, column = 0)

        page_two.incrementer = Incrementer(page_two, '1')
        page_two.incrementer.frame.grid(pady = 80)
