Surveyor
========

.. currentmodule:: tkinter_spa.surveyor

.. autoclass:: Instruction()

    **widgets** is the internal widget name used by the embedded tcl/tk interpreter and
    is returned by the ``widget.nametowidget()`` method.

    .. seealso::

        :ref:`programmatic_interaction`

.. autoclass:: Surveyor()
    
    .. automethod:: Surveyor.report_callback_exception
    
        This override ensures that an exception raised during the GUI execution does not interrupt the test session. The application is automatically closed, allowing the test to continue without manual intervention.

        :attr:`assertion_error` forwards the exception to the test once it regains control,
        allowing to raise the exception properly.

        This mechanism ensures that if the application fails, the test will also fail ; it
        maintains consistency between application state and test outcome.

        .. seealso::

            :ref:`test_with_surveyor`

    .. automethod:: Surveyor.find_widget

        .. [1] Widgets stored in memory are accessible programmatically, but the purpose
            of the Surveyor is to reproduce the user journey of a human being.
            ``winfo_ismapped()`` method returns a boolean whether the widget is visible
            on the GUI or hidden. False raises the RuntimeError.

    .. automethod:: Surveyor.execute_next_instruction

        .. seealso::
            
            :ref:`test_with_surveyor`
    
    .. automethod:: Surveyor.run_instructions

        Tkinter provides the ``after()`` method, which schedules a callable to be executed
        after a given delay, without blocking the event loop. This allows for
        recursive-style execution patterns where a function re-schedules itself, enabling
        time-based iteration within the GUI.

        This is the core mechanism used by the :class:`~tkinter_spa.surveyor.Surveyor`. Each
        instruction is executed after a delay, giving the illusion of sequential flow while
        still preserving GUI responsiveness.

        .. code-block:: python

            import tkinter as tk

            from tkinter_spa.utils.tkinter_tools import set_geometry

            def update_label():
                counter.set(counter.get() + 1)
                root.after(1000, update_label)

            root = tk.Tk()
            root.geometry(set_geometry(root, 200, 25))

            counter = tk.IntVar(value = 0)
            tk.Label(root, textvariable = counter).pack()

            update_label()

            root.mainloop()

        As you can see in this minimal example, ``after()`` allows the GUI to update the
        label over time by repeatedly invoking ``update_label()`` without freezing the
        application.

    .. note::

        In principle, calling ``self.execute_next_instruction()`` directly should be enough
        to begin the instruction sequence. However, a short delay is required to ensure that
        all widgets have been properly mapped to the screen.

        Although the application initializes and displays correctly, the widget targeted by
        the first instruction will consistently return ``False`` when checked with
        ``winfo_ismapped()``, meaning it is not yet visible to the user.

        To avoid this race condition, the first instruction must be delayed using
        ``after()``, giving the GUI time to complete its layout before interaction begins.