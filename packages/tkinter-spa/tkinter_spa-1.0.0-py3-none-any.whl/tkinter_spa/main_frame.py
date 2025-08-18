from importlib import import_module
from tkinter import ttk

from tkinter_spa.utils.path_tools import locate_directory
from tkinter_spa.utils.string_tools import module_to_class_name, title_snake_case


view_directory = locate_directory()

class SingleInstanceFactory(type):
    """
        Metaclass ensuring that only one MainFrame instance is packed at any given time.

        Attributes
        ----------
        instance : MainFrame or None
            Stores the instance of MainFrame displayed by the tkinter application.
    """

    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is not None:
            cls.instance.pack_forget()
        cls.instance = super(SingleInstanceFactory, cls).__call__(*args, **kwargs)

        return cls.instance

class MainFrame(ttk.Frame, metaclass = SingleInstanceFactory):
    """
        Custom ttk.Frame used as the main container for displaying application views.

        Parameters
        ----------
        title : str
            Title displayed in the root window's title bar when the mainframe
            is packed.
        master : tk.Tk
            The root Tkinter window.
    """

    def __init__(self, master, title):
        cnf = {
            'name': f'{self.__class__.__name__.lower()}_{title_snake_case(title)}'
        }
        self.title = title
        super().__init__(master, **cnf)
        self.bind('<Destroy>', self.reset)
        self.pack()

    def pack(self, *args, **kwargs):
        """
            Overrides the default ``pack()`` behaviour to set the window title and
            register the current instance as the active ``MainFrame``.
        """

        self.master.title(self.title)
        if MainFrame.instance is not self:
            MainFrame.instance = self
        super().pack(*args, **kwargs)

    def reset(self, event):
        """
            Event callback that resets ``MainFrame.instance`` to ``None`` when
            the widget is destroyed.
        """

        if event.widget is MainFrame.instance:
            MainFrame.instance = None

    def swap_mainframes(self, module_name):
        """
            Calls the next ``View`` subclass to pack the mainframe requested by
            the user.

            Parameters
            ----------
            module_name : str
                The name of the module in which the ``View`` subclass instantiates the
                mainframe selected for the frame swapping.
        """

        from tkinter_spa.view import View


        path_to_module = f'{view_directory}.{module_name}'
        class_name = module_to_class_name(module_name)
        module = import_module(path_to_module)
        view_instance = getattr(module, class_name)

        if not issubclass(view_instance, View):
            raise TypeError(f"{class_name} in '{module_name}.py' must subclass View.")

        view_instance(self.master)
