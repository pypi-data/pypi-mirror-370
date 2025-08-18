from tkinter_spa.surveyor import Instruction, Surveyor


# py -B -m pytest -rA -k "test_nominal_run"
def test_nominal_run(root):

    instructions = [
        Instruction('mainframe_home.!button', 'invoke'),
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
        Instruction('mainframe_coucou.frame_swapper_belle_view.!button', 'invoke')
    ]

    def check_assertions():

        home_incrementer = (
            root.nametowidget('.mainframe_home')
            .incrementer.counter.get()
        )
        belle_incrementer = (
            root.nametowidget('.mainframe_belle')
            .incrementer.counter.get()
        )
        list_values = root.nametowidget('.mainframe_coucou.!listbox').get(0, 'end')
        list_selected_value = (
            root.nametowidget('.mainframe_coucou.!listbox')
            .selection_get()
        )

        assert home_incrementer == 3
        assert belle_incrementer == 1
        assert list_values == ('yay', 'yoy', 'yuy')
        assert list_selected_value == 'yoy'

    surveyor = Surveyor(
        root, instructions,
        delay = 50, check_assertions = check_assertions
    )
    surveyor.run_instructions()

    root.mainloop()

    if surveyor.assertion_error:
        raise surveyor.assertion_error
