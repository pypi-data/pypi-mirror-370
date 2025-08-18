tkinter_spa documentation
=========================

`tkinter_spa` stands for **Tkinter (as a) Single Page Application**. It is a micro-framework
created to ease the development of tkinter application by following single page application
approach. The single page application concept consists to have an element acting as
a placeholder for contents. The contents are rendered and updated following the user
interaction with the interface.

In web application, the application loads a single web document whose body is updated
with html pages created from templates or components.

In `tkinter_spa` the application loads a ``tk.Tk`` instance, which is the main window of a standard tkinter application, that is updated with tkinter widgets.

The magic happens thanks to the interaction between :class:`~tkinter_spa.view.View` and
:class:`~tkinter_spa.main_frame.MainFrame` classes.

Regarding testings, `tkinter_spa` provides the :class:`~tkinter_spa.surveyor.Surveyor`, a tool that can interact with any tkinter applications by following a user journey scenario in the form of a list of instructions.

.. toctree::
   :maxdepth: 3

   guides/index

.. toctree::
   :maxdepth: 2

   api/index