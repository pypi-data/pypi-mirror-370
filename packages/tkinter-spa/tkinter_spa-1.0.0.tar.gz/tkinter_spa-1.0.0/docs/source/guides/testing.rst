Testing with tkinter_spa
========================

When testing a GUI, writing logic tests alone is not enough. It is better to test the application in real time to ensure it behaves as expected.

This was the reasoning behind designing a tool capable of following instructions to explore an
application, much like a webcrawler or scraper does with a website.

Thanks to tkinter's ``after()`` method, I had a starting point to imagine how a surveyor could be designed.

This section describes how to programmatically explore a tkinter GUI with the :class:`~tkinter_spa.surveyor.Surveyor`, and how to write tests that conform to this approach.

Creation and use of the instructions
------------------------------------

.. _programmatic_interaction:

Programmatic interaction with the application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A :class:`~tkinter_spa.surveyor.Surveyor` requires two things to function: a tkinter application and a list of :class:`~tkinter_spa.surveyor.Instruction`.

Each instruction corresponds to an action applied to a widget (e.g., clicking a button, entering text into an entry, etc.).

An instruction consists of a path to a specific widget, an action to perform on that widget, and optionally parameters required for that action.

A tkinter widget path is typically composed of widget names separated by dots (.), with the first dot representing the root widget (e.g., ``'.widget_1.widget_2.!button'``). It is also known as the internal widget name.

Before writing any instructions to execute on the application, it's helpful to verify that the application can actually perform the desired action. To do this, you can "walk through" a tkinter application by programmatically invoking widget actions.

An illustration is worth a hundred words:

.. code-block:: python
    :caption: demo.py

    from custom_tkinter_app import CustomTkinterApp
    from views.page_one import PageOne

    root = CustomTkinterApp().initialize(startup_view = PageOne)

    # Restaure the default behaviour on application closure
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.nametowidget('.mainframe_page_one.frame_swapper_page_two.!button').invoke()

    root.mainloop()

.. warning::
    Do not assume that this block of code runs the tkinter application programmatically.
    Instead, it modifies the initial state of the app. Such code can interact with widgets
    that are not currently visible or accessible to a human user, which defeats the purpose
    of GUI testing.

Now, for our first user journey - our first scenario - let's reproduce :ref:`this demo <permanance_object_demo>`.

.. code-block:: python
    :caption: scenarios/tutorial_run.py

    from custom_tkinter_app import CustomTkinterApp
    from views.page_one import PageOne


    # Run with "py -B -m scenarios.tutorial_run"

    root = CustomTkinterApp().initialize(startup_view = PageOne)

    # Restaure the default behaviour on application closure
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.nametowidget('.mainframe_page_one.incrementer_1.bouton').invoke()
    root.nametowidget('.mainframe_page_one.frame_swapper_page_two.!button').invoke()
    root.nametowidget('.mainframe_page_two.incrementer_1.bouton').invoke()
    root.nametowidget('.mainframe_page_two.incrementer_1.bouton').invoke()
    root.nametowidget('.mainframe_page_two.frame_swapper_page_one.!button').invoke()
    root.nametowidget('.mainframe_page_one.incrementer_1.bouton').invoke()
    root.nametowidget('.mainframe_page_one.incrementer_1.bouton').invoke()
    root.nametowidget('.mainframe_page_one.frame_swapper_page_two.!button').invoke()

    root.mainloop()

The call to ``root.mainloop()`` is optional. It runs the application in its current state,
allowing you to verify that the actions were performed as expected.

Notice that finding the path to widgets can be quite tedious. That's why `tkinter_spa` also comes with :func:`print_widget_tree() <tkinter_spa.utils.debugging.print_widget_tree>`, a dedicated tool to help explore the widget hierarchy.

.. code-block:: python
    :caption: scenarios/tutorial_run.py
    :emphasize-lines: 1, 17

    from tkinter_spa.debugging import print_widget_tree

    from custom_tkinter_app import CustomTkinterApp
    from views.page_one import PageOne


    # Run with "py -B -m scenarios.tutorial_run"

    root = CustomTkinterApp().initialize(startup_view = PageOne)

    # Restaure the default behaviour on application closure
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    # Swap to page_two to generate its widgets
    root.nametowidget('.mainframe_page_one.frame_swapper_page_two.!button').invoke()

    print_widget_tree(root)

.. code-block:: console
   :caption: Terminal output
   :emphasize-lines: 5

    .
    ├── .mainframe_page_one
    │   ├── .mainframe_page_one.!label
    │   ├── .mainframe_page_one.frame_swapper_page_two
    │   │   └── .mainframe_page_one.frame_swapper_page_two.!button <- the button clicked above
    │   └── .mainframe_page_one.incrementer_1
    │       ├── .mainframe_page_one.incrementer_1.!label
    │       └── .mainframe_page_one.incrementer_1.bouton
    └── .mainframe_page_two
        ├── .mainframe_page_two.!label
        ├── .mainframe_page_two.frame_swapper_page_one
        │   └── .mainframe_page_two.frame_swapper_page_one.!button
        └── .mainframe_page_two.incrementer_1
            ├── .mainframe_page_two.incrementer_1.!label
            └── .mainframe_page_two.incrementer_1.bouton

Using the instructions along with the surveyor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the scenario behaves as expected during the user journey, the command can be turned into
an :class:`~tkinter_spa.surveyor.Instruction` and passed to a :class:`~tkinter_spa.surveyor.Surveyor` instance.

This is a minimal example running only the first instruction of the scenario.

.. code-block:: python
    :caption: scenarios/surveyor_demo.py

    from tkinter_spa.surveyor import Instruction, Surveyor

    from custom_tkinter_app import CustomTkinterApp
    from views.page_one import PageOne


    # Run with "py -B -m scenarios.surveyor_demo"

    root = CustomTkinterApp().initialize(startup_view = PageOne)

    # Restaure the default behaviour on application closure
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    instructions = [
        Instruction('.mainframe_page_one.incrementer_1.bouton', 'invoke')
    ]

    surveyor = Surveyor(root, instructions)
    surveyor.run_instructions()

    root.mainloop()

.. raw:: html

    <figure>
        <video class="video-player-centered" controls preload="none" poster="../../_static/posters/black-poster.png">
            <source src="../../_static/gifs/surveyor-demo.mp4" type="video/mp4">
        </video>
        <figcaption>
            <p>Surveyor demo</p>
        </figcaption>
    </figure>

We saw the application run before our eyes, but that alone isn't enough to make it reliable.
How can we be sure that the incrementation actually worked? Should we pause the application and take a screenshot of the frame?

Let's learn how to integrate a surveyor with the complete scenario into an actual test suite.

How to write tests integrating the surveyor with pytest
-------------------------------------------------------

Each test must run their own instance of the tkinter application. So defining the application
as a fixture naturally suggests itself. It can be done simply by defining ``root`` the same way you would in the main entrypoint of the application.

.. code-block:: ini
    :caption: pytest.ini

    [pytest]
    ; remove unwanted plugins
    addopts = -p no:cacheprovider

    python_files = test_*.py

.. code-block:: python
    :caption: tests/confest.py
    :linenos:

    import pytest

    from custom_tkinter_app import CustomTkinterApp
    from views.page_one import PageOne


    @pytest.fixture
    def root():
        root = CustomTkinterApp().initialize(startup_view = PageOne)

        # Restaure the default behaviour on application closure
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        return root

.. tip::

    It is **crucial** to create a fresh instance of the application for each test, because
    during a pytest session, all tkinter applications run within the same Python runtime. If resources from a previous instance are not properly released or internal states are
    not fully reset, this may cause runtime errors.

    A common error would be an action failing because the application has already been destroyed.

.. _test_with_surveyor:

Barebone of a test with the surveyor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before introducing the structure of a test using the :class:`~tkinter_spa.surveyor.Surveyor`, one must understand an important aspect of integrating a graphical application like tkinter into a testing framework such as pytest.

In a test suite, pytest controls the execution flow and is responsible for collecting test results. However, a tkinter application runs its own event loop (``root.mainloop()``), which is asynchronous and independent of pytest's flow. This means that if an error occurs inside the GUI, it is not automatically propagated to the test framework.

From pytest’s perspective, calling ``root.mainloop()`` is just another function call — and once it returns, the test continues. If the GUI experienced a failure during execution (such as a widget action failing or an assertion inside the GUI logic not being met), it won't affect the test outcome unless the test explicitly raises an exception.

To overcome this limitation, tests using a surveyor instance must include two additional components beyond the instructions declaration: a ``check_assertions()`` callback, and a conditional block that raises the :attr:`Surveyor.assertion_error <tkinter_spa.surveyor.Surveyor.assertion_error>` if one occurred during execution.

.. code-block:: python
    :caption: test_barebone.py
    :emphasize-lines: 10, 18-19

    # Imports
    ...

    def test_lorem_ipsum(root):

        instructions = [
            ...
        ]

        def check_assertions():
            ...
        
        surveyor = Surveyor(root, instructions, delay = 50, check_assertions = check_assertions)
        surveyor.run_instructions()

        root.mainloop()

        if surveyor.assertion_error:
            raise surveyor.assertion_error

``check_assertions()`` serves as a dedicated scope for defining assertions that validate the
test. It is injected into the surveyor and populates the ``assertion_error`` attribute if an
assertion fails.

Accessing widget values with tkinter Variables
""""""""""""""""""""""""""""""""""""""""""""""

Some widgets, such as ``Label``, do not expose the ``tkinter.Variable`` they are bound to. A common workaround is to store a direct reference to that variable at widget creation time. With `tkinter_spa`, this is straightforward:

.. code-block:: python
    :caption: views/page_one.py
    :emphasize-lines: 14-15

    class PageOne(View):
        def __init__(self, master):
            self.master = master
            self.title = 'Page one'

        def set_view(self):
            page_one = MainFrame(self.master, self.title)

            ttk.Label(page_one, text = 'This the page one').grid(pady = (30, 15))

            page_two_swapper = FrameSwapper(page_one, 'To page two', 'page_two')
            page_two_swapper.frame.grid()

            page_one.incrementer = Incrementer(page_one, '1')
            page_one.incrementer.frame.grid(pady = (30, 0))

This pattern works naturally in Python, where traditional getter/setter methods are not required to access or mutate attributes. Attributes can be assigned dynamically to an object, making it easy to compose widgets together at runtime. In the example above, the ``Incrementer`` instance is attached to the MainFrame object via the ``incrementer`` attribute.

This kind of composition allows test code to access internal widget state directly. For example, you can retrieve the value of the ``counter`` tkinter variable associated with the ``Incrementer`` using:

.. code-block:: python

    def check_assertion()

        page_one_incrementer = root.nametowidget('.mainframe_page_one').incrementer.counter.get()

        assert page_one_incrementer == <expected_value>

Final demo
----------

.. code-block:: python
    :caption: tests/test_gui.py

    from tkinter_spa.surveyor import Instruction, Surveyor


    # py -B -m pytest -rA -k "test_tutorial_run"
    def test_tutorial_run(root):

        instructions = [
            Instruction('.mainframe_page_one.incrementer_1.bouton', 'invoke'),
            Instruction('.mainframe_page_one.frame_swapper_page_two.!button', 'invoke'),
            Instruction('.mainframe_page_two.incrementer_1.bouton', 'invoke'),
            Instruction('.mainframe_page_two.incrementer_1.bouton', 'invoke'),
            Instruction('.mainframe_page_two.frame_swapper_page_one.!button', 'invoke'),
            Instruction('.mainframe_page_one.incrementer_1.bouton', 'invoke'),
            Instruction('.mainframe_page_one.incrementer_1.bouton', 'invoke'),
            Instruction('.mainframe_page_one.frame_swapper_page_two.!button', 'invoke'),
        ]

        def check_assertions():
            page_one_incrementer = root.nametowidget('.mainframe_page_one').incrementer.counter.get()
            page_two_incrementer = root.nametowidget('.mainframe_page_two').incrementer.counter.get()

            assert page_one_incrementer == 3
            assert page_two_incrementer == 2

        surveyor = Surveyor(root, instructions, delay = 1000, check_assertions = check_assertions)
        surveyor.run_instructions()

        root.mainloop()

        if surveyor.assertion_error:
            raise surveyor.assertion_error

.. raw:: html

    <figure>
        <video class="video-player-centered" controls preload="none" poster="../../_static/posters/black-poster.png">
            <source src="../../_static/gifs/final-demo.mp4" type="video/mp4">
        </video>
        <figcaption>
            <p>GUI tested with pytest demo</p>
        </figcaption>
    </figure>

.. figure:: ../_static/screenshots/final-demo-terminal-output.png
    :alt: final demo terminal output
    :align: center
    :class: zoomable-image

    Terminal output