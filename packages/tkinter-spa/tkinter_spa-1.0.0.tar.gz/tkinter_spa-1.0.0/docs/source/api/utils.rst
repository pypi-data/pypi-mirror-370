Utilities
=========

.. autofunction:: tkinter_spa.utils.debugging.print_widget_tree

.. autofunction:: tkinter_spa.utils.path_tools.locate_directory

    This function is called at the top of the ``main_frame`` module to determine the location of the views directory.
    
    Its return value is assigned to the variable **view_directory**
    that is used in the :meth:`MainFrame.swap_mainframes() <tkinter_spa.main_frame.MainFrame.swap_mainframes>` method, avoiding recalculation the ``'views'`` directory path each time it is called.

.. autofunction:: tkinter_spa.utils.string_tools.module_to_class_name

.. autofunction:: tkinter_spa.utils.string_tools.title_snake_case

.. autofunction:: tkinter_spa.utils.tkinter_tools.set_geometry