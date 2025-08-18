Tkinter single page mechanism
=============================

The single page application approach, tkinter-like
---------------------------------------------------

A custom tkinter widget acts as a page containing components. This page is loaded on the application.

Think of it like the application is a canva. The page is the frame that organizes the disposition of the content on the canva.

Rendering different content on the main window of the application implies the
replacement of the current page by another one.

For instance, the login page would be swapped for the home page once the user is connected.

Before describing in detail the single page mechanism, it is important to introduce the
:class:`~tkinter_spa.main_frame.MainFrame` and :class:`~tkinter_spa.view.View` classes and their metaclasses, :class:`~tkinter_spa.main_frame.SingleInstanceFactory` and
:class:`~tkinter_spa.view.CallableClass`.

.. _mainframe_introduction:

Introduction of MainFrame: the head of the page
------------------------------------------------

Since the single page application approach is not natively implemented in tkinter, a mechanism
enabling it has to be designed. The canva is already present as the tkinter main window (aka.
root or application). The content on the canva is already there too thanks to the widgets.
The missing part is the page, the mainframe.

To guide the design of ``MainFrame``, the following postulates were formulated:

- only one mainframe can be displayed at a time on ``root``;
- each mainframe are unique;
- the recall of a mainframe does not create a new one, but invoke the existing one;
- the mainframes must not restrain or impact in any way the functionning of underlying tkinter widgets;

.. _single_instance_factory_introduction:

Introduction of the metaclass SingleInstanceFactory: making one and only one
----------------------------------------------------------------------------

Mainframes have two responsibilities : frame others tkinter widgets and make sure of their
uniqueness. The second responsibility is handled by a metaclass altering the way mainframes
are instanciated.

The ``SingleInstanceFactory`` ensures that only one ``MainFrame`` instance is packed at any given time.

It is only a gear of the single page mechanism that is explained in detail below.

Introduction of views: the tail of the page
-------------------------------------------

To further ease the use of mainframes, a new logic layer was added between ``root`` and
the ``MainFrame``. This layer handles the packing of a ``MainFrame`` for the developer and
provides a dedicated space to build the layout of tkinter widgets and define behaviours associated with the ``MainFrame``.

For example, a view can create widgets, bind events, open modal windows, or
integrate reusable components like buttons or counters.

Each subclass of ``View`` is tied to a single ``MainFrame`` and must implement the
:meth:`View.set_view() <tkinter_spa.view.View.set_view>` method to build the widget layout. This pattern is illustrated in the
section explaining :doc:`how to build a tkinter application with tkinter_spa <../guides/quickstart>`.

.. _view_subclasses_discovery_automation:

Discovery automation of View subclasses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Additionally, each subclass of ``View`` must be declared in its own module,
following a specific naming convention. 

Instead of requiring developers to manually register views in a central configuration file,
`tkinter_spa` uses a "structure-as-registry" approach to locate and load views automatically.

Developers organize their views by placing them in a dedicated **views** directory.
Each view is implemented in its own file.

.. important::

    1 ``MainFrame`` = 1 ``View`` subclass = 1 python file

    The name of the ``View`` subclass must match the name of its file,
    following Python naming conventions.

    For example, a view named ``HomeView`` should be defined in a file named ``home_view.py``,
    located inside the **views/** directory.

`tkinter_spa` dynamically discovers and imports these modules based on
this directory structure and naming convention. This automatic discovery allows the
application to locate and display the appropriate view without manual imports or registrations, simplifying development and reducing boilerplate.

.. seealso::

    :meth:`MainFrame.swap_mainframes() <tkinter_spa.main_frame.MainFrame.swap_mainframes>`

    :func:`locate_directory() <tkinter_spa.utils.path_tools.locate_directory>`

Introduction of CallableClass: skip boilerplate, write logic
------------------------------------------------------------

The primary goal of this design is to simplify the development of tkinter applications.
tkinter is already a complex toolkit — with its widget system and component interactions —
without also requiring developers to manually manage the views that enable the
single-page application pattern.

Just like ``View`` automatically handles the packing of ``MainFrame``, `tkinter_spa`
takes care of calling the views themselves.

This is made possible by the :class:`~tkinter_spa.view.CallableClass` metaclass.

.. _single_page_mechanism:

The single page mechanism in tkinter_spa
----------------------------------------

The single-page mechanism relies on the orchestration of packing and unpacking
``MainFrame`` instances. This logic is distributed across multiple components,
which can make it difficult to follow at first glance.

While it might seem preferable to centralize the logic in a single location,
such an approach would require overriding more of Tkinter’s native behavior
than necessary. To preserve the natural flow of tkinter applications,
`tkinter_spa` distributes responsibilities across components in a modular way.

At a high level, the mechanism involves two conceptual states:

- the **initial state**, when the ``MainFrame`` has not yet been created;
- the **recall state**, when the ``MainFrame`` already exists and is a child of ``root``;

These states are not explicitly defined in the codebase, but they can be
inferred from the logic within the ``__call__`` method of the :class:`~tkinter_spa.view.View` class.

When a ``View`` subclass is instantiated — either via the
:meth:`TkinterApp.initialize() <tkinter_spa.tk_root.TkinterApp.initialize>` method or the
:meth:`MainFrame.swap_mainframes() <tkinter_spa.main_frame.MainFrame.swap_mainframes>` method, it is instantiated
and called by the :class:`~tkinter_spa.view.CallableClass` metaclass. The ``View`` subclass
has a **title**, which corresponds to the **title** of its associated ``MainFrame``.

Upon being called, the ``View`` checks whether a child of ``root`` has a name matching its **title**.
This determines whether the application is in the initial or recall state.

- In the **initial state**, the :meth:`View.set_view() <tkinter_spa.view.View.set_view>` method is called to instantiate and configure
  the ``MainFrame``. This instantiation triggers the :class:`~tkinter_spa.main_frame.SingleInstanceFactory`
  metaclass, which sets its **instance** attribute to the new ``MainFrame``.
  If another mainframe was previously packed, it is automatically unpacked using ``pack_forget()``.
  The new ``MainFrame`` is then packed, displaying its associated widgets.

- In the **recall state**, `tkinter_spa` reuses the existing ``MainFrame`` instance still in memory.
  Since ``pack_forget()`` only hides the widget without destroying it, the view can simply
  re-pack the corresponding ``MainFrame`` without re-instantiating or re-populating it.
  This results in a seamless transition between views, maintaining the single-page experience.