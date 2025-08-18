"""
    Since root is a blank cast on which Views instances pack their widgets,
    it requires a View instance so that the user can interact with the application.
"""
from tkinter_spa.tk_root import TkinterApp

from app.views.home_view import HomeView
from app.views.page_one_view import PageOneView  # noqa: F401


root = TkinterApp().initialize(startup_view = HomeView)

root.mainloop()
