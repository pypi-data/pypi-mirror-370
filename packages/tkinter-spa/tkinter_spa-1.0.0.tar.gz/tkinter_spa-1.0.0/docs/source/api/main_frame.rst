MainFrame
=========

.. currentmodule:: tkinter_spa.main_frame

.. autoclass:: SingleInstanceFactory(type)

    For more details, read :ref:`the introduction of the metaclass SingleInstanceFactory <single_instance_factory_introduction>`.

.. autoclass:: MainFrame(ttk.Frame, metaclass = SingleInstanceFactory)

    The **title** is also used to customised the name of the widget using **cnf**.

    In tkinter, **cnf** is the dictionnary providing configuration options for a tkinter
    widget. In this case, it is used in order to customised the name of the ``MainFrame`` as a
    widget.

    For instance, a mainframe initialized with the **title** ``'home'`` will be found
    at ``root.winfo_children()`` as ``'mainframe_home'``.

    In addition to that, the constructor also use the bind method, common to every tkinter
    widgets, to alter the behaviour of the widget on the call of the event ``'<Destroy>'``.
    The ``'<Destroy>'`` event occurs when the widget is destroyed, either by the user manually
    clicking on the close button of the GUI or when the parent of the widget is undergoing
    the ``'<Destroy>'`` event.
    The behaviour of the widget is altered by the :meth:`reset() <tkinter_spa.main_frame.MainFrame.MainFrame.reset>` method.

    .. automethod:: MainFrame.pack

        The ``MainFrame`` plays a dual role: it is both a ``ttk.Frame`` attached to the
        root window and the main container associated with a ``View`` subclass.

        Because it acts as the visible content of the application, it cannot behave
        like a regular widget when packed.

        This method ensures that before the ``MainFrame`` is packed, it updates the 
        title of the window and stores itself as the active instance using the metaclass
        attribute. This allows `tkinter_spa` to keep track of which frame is currently
        visible.

    .. automethod:: MainFrame.reset

        Before the tkinter application shuts down, all widgets are destroyed gracefully,
        from children to parent, up to the root.

        While this behavior works as intended for most widgets, it is not sufficient for
        mainframes. By design, mainframes are singular: calling their constructor returns
        the same instance if one already exists. This mechanism relies on a class attribute
        from the ``SingleInstanceFactory`` metaclass, which is not a tkinter widget.

        As a result, when the tkinter application shuts down, a reference to the last
        created ``MainFrame`` instance remains in the Python runtime environment.

        For end users, this is not an issue, as closing the tkinter application typically
        coincides with terminating the Python runtime. However, in a test environment where
        each test creates a new tkinter application within the same Python runtime,
        successive tests may unintentionally share the same ``MainFrame`` instance.

        This leads to errors, as the application logic may try to access widgets under
        ``root`` when none exist anymore.

        To ensure that subsequent tkinter applications starts from a clean state within the
        same Python runtime, the ``reset()`` method is registered as an event handler for
        the ``<Destroy>`` event. This method resets ``MainFrame.instance`` back to ``None``,
        restoring the class to its initial state.

    .. automethod:: MainFrame.swap_mainframes

        In order to perform redirections between views, each one must reference other views.
        This creates a circular import issue when trying to import ``View`` subclasses directly.

        To resolve this, the ``swap_mainframes()`` method performs dynamic imports based on naming conventions. It uses the title of the target view to locate and instantiate the appropriate ``View`` subclass without requiring direct imports, thereby avoiding circular dependencies.

        For more details, read :ref:`how tkinter_spa discovers view subclasses <view_subclasses_discovery_automation>`.