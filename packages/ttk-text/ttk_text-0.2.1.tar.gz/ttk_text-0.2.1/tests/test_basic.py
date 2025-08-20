from tkinter.ttk import Button, Entry, Style

import pytest


def test_state_focus(themed_texts):
    text1, text2 = themed_texts
    text1.focus()
    text1.update()
    assert "focus" in text1.frame.state()
    assert "focus" not in text2.frame.state()
    text2.focus()
    text2.update()
    assert "focus" not in text1.frame.state()
    assert "focus" in text2.frame.state()


def test_inheritance(themed_text):
    from tkinter import Text
    assert isinstance(themed_text, Text)


def test_path(themed_text):
    assert str(themed_text) == str(themed_text.frame)


def test_configuration(app, style):
    from ttk_text import ThemedText
    style.theme_use("classic")
    app.update_idletasks()
    text = ThemedText(app, background="red", foreground="blue")
    text.pack()
    assert text.cget("background") == "red"
    assert text.cget("foreground") == "blue"
    assert text.cget("selectbackground") == style.lookup("TEntry", "selectbackground", ["focus"])
    assert text.cget("selectforeground") == style.lookup("TEntry", "selectforeground", ["focus"])
    text.configure(background="black", foreground="white", selectbackground="gray", selectforeground="black")
    style.theme_use("clam")
    app.update_idletasks()
    assert text.cget("background") == "black"
    assert text.cget("foreground") == "white"
    assert text.cget("selectbackground") == "gray"
    assert text.cget("selectforeground") == "black"
