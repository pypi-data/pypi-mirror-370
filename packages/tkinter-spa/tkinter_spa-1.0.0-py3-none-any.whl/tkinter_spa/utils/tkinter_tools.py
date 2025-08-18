def set_geometry(parent, width, height):
    """
        Computes the geometry string to center a window on the screen.

        Parameters
        ----------
        parent : tkinter.Tk or tkinter.Toplevel
            The parent window used to retrieve screen dimensions.
        width : int
            The desired width of the window.
        height : int
            The desired height of the window.

        Returns
        -------
        str
            A geometry string formatted as "WxH+X+Y" to center the window.
    """
    return (
        f'{width}x{height}+'
        f'{parent.winfo_screenwidth() // 2 - width // 2}+'
        f'{parent.winfo_screenheight() // 2 - height // 2}'
    )
