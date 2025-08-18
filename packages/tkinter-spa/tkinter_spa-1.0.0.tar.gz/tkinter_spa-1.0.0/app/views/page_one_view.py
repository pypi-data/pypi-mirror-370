from tkinter import ttk

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.view import View

from app.components.clicker import Incrementer
from app.components.frame_swapper import FrameSwapper


class PageOneView(View):
    def __init__(self, master):
        self.master = master
        self.title = 'Page one'

    def set_view(self):
        page_one = MainFrame(self.master, self.title)

        ttk.Label(page_one, text = "This the page one").grid(row = 0)

        page_two_swapper = FrameSwapper(page_one, 'to page two', 'page_two_view')
        page_two_swapper.frame.grid(row = 1, column = 0)

        belle_swapper = FrameSwapper(page_one, 'vers belle', 'belle_view')
        belle_swapper.frame.grid(row = 1, column = 1)

        page_one.incrementer = Incrementer(page_one, '1')
        page_one.incrementer.frame.grid(pady = 80)
