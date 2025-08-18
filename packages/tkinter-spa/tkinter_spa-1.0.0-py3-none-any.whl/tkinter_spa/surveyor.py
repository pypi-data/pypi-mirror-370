class Instruction():
    """
        Defines the elements required to perform an action on a Tkinter widget.

        Parameters
        ----------
        widgets : str
            A widget path used to locate the target widget in the widget hierarchy.
        action : str
            The name of the Tkinter method (e.g. 'invoke', 'get', 'insert') to call on
            the widget.
        parameters : tuple, optional
            Parameters required for specific actions. Defaults to None.
    """

    def __init__(self, widgets, action, parameters = None):
        self.widgets = self.split_widgets(widgets)
        self.action = action
        self.parameters = parameters

    def split_widgets(self, widgets):
        """
            Splits the name of the widgets and excludes root

            Returns
            -------
            list[str]
        """
        return widgets.strip('.').split('.')

class Surveyor():
    """
        Automates the execution of a user journey by following a sequence of
        instructions on a tkinter application.

        Parameters
        ----------
        root : tk.Tk
            The root window of the tkinter application.
        instructions: list[Instruction]
            A list of instructions to execute during the exploration of the application.
        delay : int
            Delay in milliseconds between the execution of each instruction.
        check_assertions : callable, optional
            A function called after all instructions have been executed.
            Defaults to None.

        Attributes
        ----------
        steps : int
            The number of instructions to execute.
        current_step : int
            The index of the current instruction being executed.
        assertion_error : Exception or None
            Stores any exception raised during the execution. If not None, the
            exception can be re-raised by the test framework.
    """

    def __init__(self, root, instructions, delay = 1000, check_assertions = None):
        self.root = root
        self.instructions = instructions
        self.steps = len(instructions)
        self.current_step = 0
        self.delay = delay
        self.check_assertions = check_assertions
        self.assertion_error = None

        self.root.report_callback_exception = self.report_callback_exception

    def report_callback_exception(self, exc, val, tb):
        """
            Overrides the default ``tk.Tk.report_callback_exception()`` error handler
            to intercept exceptions during execution.

            When an exception is raised, it is stored in :attr:`assertion_error` and the
            application is gracefully terminated.
        """
        import traceback

        traceback.print_exception(exc, val, tb)

        self.assertion_error = val
        self.root.destroy()

    def find_widget(self, widgets):
        """
            Reach the widget required to perform the action of an Instruction instance.

            Parameters
            ----------
            widgets: list[str]
                The widgets attribute of an Instruction instance.

            Raises
            ------
            RuntimeError
                The surveyor encountered a hidden widget [1]_.
            KeyError
                Next widget not found among children of one of the current widget.
        """
        widget = self.root

        try:
            for child in widgets:
                widget = widget.children[child]

            if widget.winfo_ismapped():
                return widget
            else:
                raise RuntimeError(
                    f"User cannot interact with hidden widget: {' > '.join(widgets)}"
                )

        except KeyError:
            raise KeyError(f'Widget {child} not found in {widgets}')

    def execute_next_instruction(self):
        """
            Retrieves the corresponding widget, performs the specified action
            (optionally with parameters) and schedules the next instruction after
            a delay.

            Once all instructions are executed, runs the ``check_assertion()`` callback
            used to evaluate assertions within a test context and finally close
            the application gracefully.

            Raises
            ------
            AttributeError
                Raised if the specified action cannot be called on the target widget.
        """
        if self.current_step < self.steps:
            instruction = self.instructions[self.current_step]

            widget = self.find_widget(instruction.widgets)

            if instruction.action:
                try:
                    action = getattr(widget, instruction.action)
                except AttributeError:
                    raise AttributeError(
                        f'Action {instruction.action} not available for {widget}.'
                    )

                if instruction.parameters:
                    action(*instruction.parameters)
                else:
                    action()

            self.current_step += 1

            self.root.after(self.delay, self.execute_next_instruction)
        else:
            if self.check_assertions:
                try:
                    self.check_assertions()
                except Exception as e:
                    self.assertion_error = e

            self.root.destroy()

    def run_instructions(self):
        """
            Initiates the instruction sequence by scheduling the first call
            to :meth:`execute_next_instruction`, which starts the automated
            exploration of the application.
        """
        self.root.after(self.delay, self.execute_next_instruction)
