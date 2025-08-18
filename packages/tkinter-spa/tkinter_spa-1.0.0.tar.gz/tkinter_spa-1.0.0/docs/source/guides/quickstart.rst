Quickstart
==========

Before creating your first app, a few things to considerate:

The single page mechanism is possible by the use of ``MainFrame`` and ``View`` classes. So to begin, let's create the first page of the application.

To create a page, start by creating a **views** directory. This directory
acts as a registry of all the pages in your tkinter application.

For more details, read :ref:`how tkinter_spa discovers view subclasses <view_subclasses_discovery_automation>`.

Page creation
-------------

In this directory, we can create a file in which the first ``View`` subclass is declared, like so:

.. code-block:: python
    :caption: views/page_one.py

    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View


    class PageOne(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page one'

        def set_view(self):
        ...

To initialize it, we need the tkinter ``root`` as **master** and a **title** to display at the top. The layout of the widgets is created within the :meth:`View.set_view() <tkinter_spa.view.View.set_view>` method. To fully respect the single page approach,
the first widget to declare must be a ``MainFrame``. The ``MainFrame`` is a special tkinter widget created for `tkinter_spa`.

Learn more about its purpose in :ref:`the raison d'être of a MainFrame <mainframe_introduction>`.

.. code-block:: python
    :caption: views/page_one.py
    :emphasize-lines: 9

    ...

    class PageOne(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page one'

        def set_view(self):
            page_one = MainFrame(self.master, self.title)

This is the bare minimum to create a view, which is necessary to initiate the tkinter
application with `tkinter_spa`, like so:

.. code-block:: python
    :caption: main.py

    from tkinter_spa.tk_root import TkinterApp

    from views.page_one import PageOne

    root = TkinterApp().initialize(startup_view = PageOne)

    root.mainloop()

.. figure:: ../_static/screenshots/page-one-blank.png
    :alt: page one blank
    :align: center

    tkinter_spa application with an empty mainframe


`PageOne` displays the ``MainFrame`` successfully, as you can notice with the title of the
mainframe at the top of the window.

*Think of it like the mainframe took the hand over the application*.

You can also notice that the size of the window is quite large, without setting
any width or height. This is because `tkinter_spa` sets a default size. It is possible to
alter it quickly like so:

.. code-block:: python
    :caption: main.py
    :emphasize-lines: 7

    from tkinter_spa.tk_root import set_geometry, TkinterApp
    from views.page_one import PageOne


    root = TkinterApp().initialize(startup_view = PageOne)

    root.geometry(set_geometry(root, 250, 300))

    root.mainloop()

We can define geometry and bind protocols in a cleaner way at the end of this tutorial.

Building of the widget layout
-----------------------------

It's a bit empty though... why not add a label?

.. code-block:: python
    :caption: views/page_one.py
    :emphasize-lines: 6

    ...

    def set_view(self):
        page_one = MainFrame(self.master, self.title)

        ttk.Label(page_one, text = 'This is page one').grid(row = 0, pady = (30, 15))

.. figure:: ../_static/screenshots/page-one-label.png
    :alt: page one label
    :align: center

    Mainframe with a label

Pretty straightforward. Notice that you can place the widget anywhere within the mainframe using ``grid()``.
It's more precise than ``pack()`` and the mainframe make sure everything stay centered, because the mainframe is packed!

Switch from one page to another
-------------------------------

`tkinter_spa` behaves just like any tkinter application so far, how about we try to change
the view? After all, what is the point of a single page application if there is only
one page?!

Thankfully, ``MainFrame`` comes with a handy method for this case: :meth:`MainFrame.swap_mainframes() <tkinter_spa.main_frame.MainFrame.swap_mainframes>`.
As the name implies, it enables the swap between the mainframe currently displayed with another.

Let's create another view, called ``page_two``, and see if we can switch to it from ``page_one`` and switch back again.

.. code-block:: python
    :caption: views/page_two.py

    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View


    class PageTwo(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page two'

        def set_view(self):
            page_two = MainFrame(self.master, self.title)

            ttk.Label(page_two, text = 'This is page two').grid(row = 0, pady = (30, 15))

            ttk.Button(page_two,
                text = f'To page one', cursor = 'hand2',
                command = lambda: page_two.swap_mainframes('page_one')
            ).grid(row = 1, column = 0)

.. code-block:: python
    :caption: views/page_one.py
    :emphasize-lines: 17-20

    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View


    class PageOne(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page one'

        def set_view(self):
            page_one = MainFrame(self.master, self.title)

            ttk.Label(page_one, text = 'This is page one').grid(row = 0, pady = (30, 15))

            ttk.Button(page_one,
                text = f'To page two', cursor = 'hand2',
                command = lambda: page_one.swap_mainframes('page_two')
            ).grid(row = 1, column = 0)

:meth:`MainFrame.swap_mainframes() <tkinter_spa.main_frame.MainFrame.swap_mainframes>` takes as argument the name of the module where the ``View`` subclass
instantiates the selected ``MainFrame`` (e.g. if the selected ``MainFrame`` is in `PageTwo`, write the name of the module where `PageTwo` is defined).

.. raw:: html

    <figure>
        <video class="video-player-centered" controls preload="none" poster="../../_static/posters/swap-mainframes-poster.png">
            <source src="../../_static/gifs/swap-mainframes-demo.mp4" type="video/mp4">
        </video>
        <figcaption>
            <p>MainFrame.swap_mainframes() demo</p>
        </figcaption>
    </figure>

Object permanence in tkinter_spa
--------------------------------

Let's keep challenging `tkinter_spa`. What happens if we add one incrementer on page one and another
on page two?

.. code-block:: python
    :caption: views/page_one.py
    :emphasize-lines: 24-31

    import tkinter as tk
    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View


    class PageOne(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page one'
            self.counter = tk.IntVar()

        def set_view(self):
            page_one = MainFrame(self.master, self.title)

            ttk.Label(page_one, text = 'This the page one').grid(row = 0, pady = (30, 15))

            ttk.Button(page_one,
                text = f'To page two', cursor = 'hand2',
                command = lambda: page_one.swap_mainframes('page_two')
            ).grid(row = 1)

            frame = ttk.Frame(page_one)
            ttk.Label(frame, textvariable = self.counter)\
            .grid(row = 2, column = 0, padx = (0, 5))
            ttk.Button(frame,
                name = 'bouton', text = 'Cliquez', cursor = 'hand2',
                command = self.increment
            ).grid(row = 2, column = 1, padx = (5, 0))
            frame.grid(pady = (30, 0))

        def increment(self):
            self.counter.set(self.counter.get() + 1)

.. code-block:: python
    :caption: views/page_two.py
    :emphasize-lines: 24-31

    import tkinter as tk
    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View


    class PageTwo(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page two'
            self.counter = tk.IntVar()

        def set_view(self):
            page_two = MainFrame(self.master, self.title)

            ttk.Label(page_two, text = 'This the page two').grid(row = 0, pady = (30, 15))

            ttk.Button(page_two,
                text = f'To page one',cursor = 'hand2',
                command = lambda: page_two.swap_mainframes('page_one')
            ).grid(row = 1)

            frame = ttk.Frame(page_two)
            ttk.Label(frame, textvariable = self.counter)\
            .grid(row = 2, column = 0, padx = (0, 5))
            ttk.Button(frame,
                name = 'bouton', text = 'Cliquez', cursor = 'hand2',
                command = self.increment
            ).grid(row = 2, column = 1, padx = (5, 0))
            frame.grid(pady = (30, 0))

        def increment(self):
            self.counter.set(self.counter.get() + 1)

.. _permanance_object_demo:

.. ghost_paragraph::

.. raw:: html

    <figure>
        <video class="video-player-centered" controls preload="none" poster="../../_static/posters/incrementers-poster.png">
            <source src="../../_static/gifs/incrementers-demo.mp4" type="video/mp4">
        </video>
        <figcaption>
            <p>Object permanence demo</p>
        </figcaption>
    </figure>

As you can see, `tkinter_spa` preserves the state of the widgets even after a swap! This is because the swap mainframes design relies on
packing and unpacking mainframes, not destroying them. This design choice is key to :ref:`the single page mechanism <single_page_mechanism>`.

Even with only a handful of widgets, the layout is already starting to look cluttered.
But one of the great strengths of `tkinter_spa` is that you can integrate your own widget organization, as long as you keep ``MainFrame`` as the parent between your widgets and ``root``.

On my part, I followed the philosophy of Javascript front-end by creating reusable components.

Compose components using tkinter widgets
----------------------------------------

By design tkinter widgets are elementary units. So combining them to create more elaborate
front-end elements felt like a natural evolution.

.. code-block:: python
    :caption: components/frame_swapper.py

    from tkinter import ttk


    class FrameSwapper():
        def __init__(self, parent, text, module_name):
            self.parent = parent
            self.frame = self.set_component(text, module_name)

        def set_component(self, text, module_name):
            frame = ttk.Frame(self.parent, name = f'frame_swapper_{module_name}')
            ttk.Button(frame,
                text = text, cursor = 'hand2',
                command = lambda: self.parent.swap_mainframes(module_name)
            ).grid(row = 1, column = 0)

            return frame

.. code-block:: python
    :caption: components/clicker.py

    import tkinter as tk

    from tkinter import ttk


    class Incrementer():
        def __init__(self, parent, name):
            self.parent = parent
            self.name = f'incrementer_{name}'
            self.counter = tk.IntVar()
            self.frame = self.set_component()

        def set_component(self):
            frame = ttk.Frame(self.parent, name = self.name)
            ttk.Label(frame, textvariable = self.counter).grid(column = 0, row = 1, padx = 15)
            ttk.Button(frame,
                name = 'bouton', text = 'Cliquez', cursor = 'hand2',
                command = self.increment
            ).grid(column = 1, row = 1)

            return frame

        def increment(self):
            self.counter.set(self.counter.get() + 1)

.. code-block:: python
    :caption: views/page_one.py

    import tkinter as tk
    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View

    from components.clicker import Incrementer
    from components.frame_swapper import FrameSwapper


    class PageOne(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page one'

        def set_view(self):
            page_one = MainFrame(self.master, self.title)

            ttk.Label(page_one, text = 'This the page one').grid(row = 0, pady = (30, 15))

            page_two_swapper = FrameSwapper(page_one, 'To page two', 'page_two')
            page_two_swapper.frame.grid(row = 1)

            incrementer = Incrementer(page_one, '1')
            incrementer.frame.grid(pady = (30, 0))

.. code-block:: python
    :caption: views/page_two.py

    import tkinter as tk
    from tkinter import ttk

    from tkinter_spa.main_frame import MainFrame
    from tkinter_spa.view import View

    from components.clicker import Incrementer
    from components.frame_swapper import FrameSwapper


    class PageTwo(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page two'

        def set_view(self):
            page_two = MainFrame(self.master, self.title)

            ttk.Label(page_two, text = 'This the page two').grid(row = 0, pady = (30, 15))

            page_one_swapper = FrameSwapper(page_two, 'To page one', 'page_one')
            page_one_swapper.frame.grid(row = 1)

            incrementer = Incrementer(page_two, '1')
            incrementer.frame.grid(pady = (30, 0))

To complete this tutorial, let's explore how to customize :class:`~tkinter_spa.tk_root.TkinterApp` to add custom behaviour like geometry or protocol bindings to the ``root`` window.

.. _customize_root:

Customize the root initialization
---------------------------------

Up to now, the application entry point looks like this:

.. code-block:: python
    :caption: main.py

    from tkinter_spa.tk_root import set_geometry, TkinterApp
    from views.page_one import PageOne


    root = TkinterApp().initialize(startup_view = PageOne)

    root.geometry(set_geometry(root, 250, 300))

    root.mainloop()

Which is not really ideal for managing additional behaviours or configurations to the ``root`` window. The correct solution is to create a custom :class:`~tkinter_spa.tk_root.TkinterApp` subclass that overrides the :meth:`TkinterApp.initialize() <tkinter_spa.tk_root.TkinterApp.initialize>` method.

For demonstration purpose, let’s move the geometry configuration into the subclass and
bind the ``"WM_DELETE_WINDOW"`` protocol to open a confirmation dialog when the user attempts to close the application.

.. code-block:: python
    :caption: custom_tkinter_app.py

    import tkinter as tk

    from tkinter_spa.tk_root import set_geometry, TkinterApp

    from components.confirm_quit import ConfirmQuit


    class CustomTkinterApp(TkinterApp):

        def initialize(self, startup_view):
            super().initialize(startup_view)
            self.root.geometry(set_geometry(self.root, 250, 300))
            self.root.protocol("WM_DELETE_WINDOW", self.confirm_quit)

            return self.root

        def confirm_quit(self):
            window = tk.Toplevel(name = 'quit_confirmation')
            window.title('Are you sure?')
            window.geometry(set_geometry(self.root, 300, 75))

            ConfirmQuit(window).frame.pack()

.. code-block:: python
    :caption: components/confirm_quit.py

    from tkinter import ttk


    class ConfirmQuit():
        def __init__(self, parent):
            self.parent = parent
            self.frame = self.set_component()

        def set_component(self):
            ttk.Label(self.parent, text = "Are you sure you want to quit?").pack(pady = 10)

            frame = ttk.Frame(self.parent)
            ttk.Button(frame,
                text = 'Yes', cursor = 'hand2',
                command = self.leave
            ).grid(row = 1, column = 0, padx = (0, 30))

            ttk.Button(frame,
                text = 'No', cursor = 'hand2',
                command = self.cancel
            ).grid(row = 1, column = 1, padx = (30, 0))

            return frame
        
        def leave(self):
            self.parent.master.destroy()

        def cancel(self):
            self.parent.destroy()

.. code-block:: python
    :caption: main.py

    from views.page_one import PageOne

    from custom_tkinter_app import CustomTkinterApp


    root = CustomTkinterApp().initialize(startup_view = PageOne)

    root.mainloop()

.. raw:: html

    <figure>
        <video class="video-player-centered" controls preload="none" poster="../../_static/posters/quit-protocol-poster.png">
            <source src="../../_static/gifs/quit-protocol-demo.mp4" type="video/mp4">
        </video>
        <figcaption>
            <p>Confirmation before application closure demo</p>
        </figcaption>
    </figure>

That's it for the quickstart tutorial! This simple tkinter application has demonstrated the
potential behind `tkinter_spa` framework and introduced a way of using it properly.

`tkinter_spa` also comes with a handy feature to test the integrity of a user journey into the
GUI: the Surveyor.

Learn :doc:`how to test a tkinter application's GUI with the Surveyor <../guides/testing>`.