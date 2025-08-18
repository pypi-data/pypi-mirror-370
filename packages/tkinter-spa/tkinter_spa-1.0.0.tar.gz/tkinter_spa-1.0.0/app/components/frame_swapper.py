from tkinter import ttk


class FrameSwapper():
    def __init__(self, parent, text, module_name):
        self.parent = parent
        self.frame = self.set_component(text, module_name)

    def set_component(self, text, module_name):
        frame = ttk.Frame(self.parent, name = f'frame_swapper_{module_name}')
        ttk.Button(
            frame, text = text, cursor = 'hand2',
            command = lambda: self.parent.swap_mainframes(module_name)
        ).grid(row = 1, column = 0)

        return frame
