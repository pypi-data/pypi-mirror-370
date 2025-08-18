# tkinter_spa

[![pipeline status](https://gitlab.com/wbarillon/tkinter_spa/badges/main/pipeline.svg?key_text=🔄+Pipeline+status&key_width=113)](https://gitlab.com/wbarillon/tkinter_spa/-/commits/main)
[![coverage report](https://gitlab.com/wbarillon/tkinter_spa/badges/main/coverage.svg?key_text=✅+Coverage+report&key_width=122)](https://gitlab.com/wbarillon/tkinter_spa/-/commits/main)

*tkinter_spa* stands for **Tkinter (as a) Single Page Application**. It is a micro-framework
created to ease the development of tkinter application by following single page application
approach. The single page application concept consists to have an element acting as
a placeholder for contents. The contents are rendered and updated following the user
interaction with the interface.

In [web application](https://developer.mozilla.org/en-US/docs/Glossary/SPA), the application loads a single web document whose body is updated
with html pages created from templates or components.

In *tkinter_spa* the application loads a `tk.Tk` instance, which is the main window of a standard tkinter application, that is updated with tkinter widgets.

The magic happens thanks to the interaction between **[View](https://wbarillon.gitlab.io/tkinter_spa/api/view/)** and **[MainFrame](https://wbarillon.gitlab.io/tkinter_spa/api/main_frame/)** classes.

Regarding testings, *tkinter_spa* provides the **[Surveyor](https://wbarillon.gitlab.io/tkinter_spa/api/surveyor/)**, a tool that can interact with any tkinter applications by following a user journey scenario in the form of a list of instructions.

## Installation

```
pip install tkinter-spa
```

## Usage

For a quick grasp on what *tkinter_spa* do and how to use it, check the [quickstart](https://wbarillon.gitlab.io/tkinter_spa/guides/quickstart/).

Interested in testing the GUI of your tkinter application? Check [how it's done](https://wbarillon.gitlab.io/tkinter_spa/guides/testing/) with *tkinter_spa*.

## Links

[Documentation](https://wbarillon.gitlab.io/tkinter_spa/)

## License

*tkinter_spa* is licensed under the MIT License, which permits use, copying, modification, and
distribution.
