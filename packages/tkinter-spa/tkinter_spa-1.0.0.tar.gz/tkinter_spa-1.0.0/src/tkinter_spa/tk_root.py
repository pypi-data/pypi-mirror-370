import tkinter as tk

from tkinter_spa.utils.tkinter_tools import set_geometry


class TkinterApp():
    """
        Encapsulates the root window of a Tkinter application and simplifies the
        initialization of a `tkinter_spa`-based app.

        Attributes
        ----------
        root : tk.Tk
    """
    def __init__(self):
        self.root = tk.Tk()

    def initialize(self, startup_view):
        """
            Prepares the root window and launches the given ``View`` subclass.

            Sets the initial geometry of the window and allows for
            additional root-level configurations such as protocol bindings.

            Parameters
            ----------
            startup_view : View subclass
                The first view to display when the application starts.

            Returns
            -------
            tk.Tk
                The root Tkinter window.
        """
        self.root.geometry(set_geometry(self.root, 500, 500))
        startup_view(self.root)
        return self.root
