import pytest


@pytest.fixture(scope="session")
def app():
    import tkinter as tk
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture(scope="session")
def style(app):
    from tkinter.ttk import Style
    yield Style(app)


@pytest.fixture
def themed_text(app):
    from ttk_text import ThemedText
    text = ThemedText(app)
    text.pack()
    yield text
    text.pack_forget()
    text.destroy()


@pytest.fixture
def themed_texts(app):
    from ttk_text import ThemedText
    text1 = ThemedText(app)
    text1.pack()
    text2 = ThemedText(app)
    text2.pack()
    yield [text1, text2]
    text1.pack_forget()
    text1.destroy()
    text2.pack_forget()
    text2.destroy()


@pytest.fixture
def scrolled_text(app):
    from ttk_text.scrolled_text import ScrolledText
    text = ScrolledText(app, vertical=True, horizontal=True)
    text.pack()
    yield text
    text.pack_forget()
    text.destroy()
