from abc import ABC, ABCMeta, abstractmethod

from tkinter_spa.main_frame import MainFrame
from tkinter_spa.utils.string_tools import title_snake_case


class CallableClass(ABCMeta):
    """
        Metaclass that allows a class to be instantiated and immediately called.

        For example, calling ``HomeView()`` will both instantiate the class and execute
        its ``__call__()`` method.
    """

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance()

class View(ABC, metaclass = CallableClass):
    """
        Contains the core mechanism that swaps mainframes in the application.

        If the ``MainFrame`` is a child of ``root``, the current ``MainFrame`` instance
        is swapped with the one tied to the called ``View`` subclass.

        Otherwise, the ``set_view()`` method is called to create the tied ``MainFrame``
        and its tkinter widgets.

        Attributes
        ----------
        master : tk.Tk
    """

    def __call__(self):
        for child in self.master.winfo_children():
            if child.winfo_name() == f'mainframe_{title_snake_case(self.title)}':
                MainFrame.instance.pack_forget()
                child.pack()
                return
        self.set_view()

    @abstractmethod
    def set_view(self):
        """
            Defines the layout of the view by creating and organizing tkinter widgets.

            This method serves as a dedicated scope for the developer to set up
            the associated ``MainFrame`` and its contents.

            Raises
            ------
            TypeError
                Subclass must define the ``set_view()`` method.
        """

        ...
