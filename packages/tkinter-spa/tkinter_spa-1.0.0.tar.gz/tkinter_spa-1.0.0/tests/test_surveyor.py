import pytest

from tkinter_spa.surveyor import Instruction, Surveyor

# https://docs.python.org/fr/3.13/library/operator.html#operator.methodcaller


# py -B -m pytest -rA -k "test_hidden_widgets"
def test_hidden_widgets(root):

    instructions = [
        Instruction('mainframe_home.!button', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.frame_swapper_belle_view.!button', 'invoke'),
        Instruction('mainframe_belle.incrementer_1.bouton', 'invoke'),
        Instruction('home_detail', 'destroy'),
        # Instruction cassée
        Instruction('mainframe_home.frame_swapper_coucou_view.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yay')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yoy')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yuy')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!listbox', 'selection_set', ([1])),
    ]

    surveyor = Surveyor(root, instructions, 50)
    surveyor.run_instructions()

    root.mainloop()

    with pytest.raises(RuntimeError):
        root.mainloop()

        if surveyor.assertion_error:
            raise surveyor.assertion_error

# py -m pytest -rA -k "test_wrong_action"
def test_wrong_action(root):

    instructions = [
        # Instruction cassée
        Instruction('mainframe_home.!button', 'invok'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.frame_swapper_belle_view.!button', 'invoke'),
        Instruction('mainframe_belle.incrementer_1.bouton', 'invoke'),
        Instruction('home_detail', 'destroy'),
        Instruction('mainframe_belle.frame_swapper_coucou_view.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yay')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yoy')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yuy')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!listbox', 'selection_set', ([1])),
    ]

    surveyor = Surveyor(root, instructions, 50)
    surveyor.run_instructions()

    with pytest.raises(AttributeError):
        root.mainloop()

        if surveyor.assertion_error:
            raise surveyor.assertion_error

# py -m pytest -rA -k "test_wrong_widgets"
def test_wrong_widgets(root):

    instructions = [
        # Instruction cassée
        Instruction('mainframe_home.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke'),
        Instruction('mainframe_home.frame_swapper_belle_view.!button', 'invoke'),
        Instruction('mainframe_belle.incrementer_1.bouton', 'invoke'),
        Instruction('home_detail', 'destroy'),
        Instruction('mainframe_belle.frame_swapper_coucou_view.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yay')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yoy')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!entry', 'insert', ('end', 'yuy')),
        Instruction('mainframe_coucou.!button', 'invoke'),
        Instruction('mainframe_coucou.!listbox', 'selection_set', ([1])),
    ]

    surveyor = Surveyor(root, instructions, 50)
    surveyor.run_instructions()

    with pytest.raises(KeyError):
        root.mainloop()

        if surveyor.assertion_error:
            raise surveyor.assertion_error

# py -B -m pytest -rA -k "test_assertion_error"
def test_assertion_error(root):

    instructions = [
        Instruction('mainframe_home.incrementer_1.bouton', 'invoke')
    ]

    def check_assertions():

        home_incrementer = root.children['mainframe_home'].incrementer.counter.get()

        assert home_incrementer == 3

    surveyor = Surveyor(
        root, instructions, delay = 50,
        check_assertions = check_assertions
    )
    surveyor.run_instructions()

    with pytest.raises(AssertionError):
        root.mainloop()

        if surveyor.assertion_error:
            raise surveyor.assertion_error
