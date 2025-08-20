from tkinter import Event, EventType, Grid, Pack, Place, Text
from tkinter.ttk import Frame, Style
from typing import Any, Dict

from ttk_text.utils import parse_padding

__all__ = ["ThemedText"]

_DYNAMIC_OPTIONS_TEXT = {"background", "foreground", "selectbackground", "selectforeground", "insertwidth", "font",
                         "padding"}


class ThemedText(Text):
    """
    A themed text widget combining Tkinter Text with ttk Frame styling.

    This widget provides native Tkinter Text functionality with ttk theme support.
    Inherits from `tkinter.Text` while embedding a ttk.Frame for style management.

    Style Elements:
        - Style name: 'ThemedText.TEntry' (configurable via style parameter)
        - Theme states: [focus, hover, pressed] with automatic state transitions

    Default Events:
        <FocusIn>       - Activates focus styling
        <FocusOut>      - Deactivates focus styling
        <Enter>         - Applies hover state
        <Leave>         - Clears hover state
        <ButtonPress-1> - Sets pressed state (left mouse down)
        <ButtonRelease-1> - Clears pressed state (left mouse up)
        <<ThemeChanged>> - Handles theme reload events

    Geometry Management:
        Proxies all ttk.Frame geometry methods (pack/grid/place) while maintaining
        native Text widget functionality. Use standard geometry managers as with
        regular ttk widgets.

    Inheritance Chain:
        ThemedText → tkinter.Text → tkinter.Widget → tkinter.BaseWidget → object
    """

    def __init__(self, master=None, *, relief=None, style="ThemedText.TEntry", class_="ThemedTextFrame", **kwargs):
        """Initialize a themed text widget.

        :param master: Parent widget (default=None)
        :param relief: Frame relief style (None for theme default)
        :param style: ttk style name (default='TextFrame.TEntry')
        :param class_: Widget class name (default='TextFrame')
        :param kw: Additional Text widget configuration options
        """
        self.frame = Frame(
            master,
            relief=relief,
            style=style,
            class_=class_,
            padding=kwargs.pop("padding") if "padding" in kwargs else None,
            borderwidth=kwargs.pop("borderwidth") if "borderwidth" in kwargs else None
        )
        Text.__init__(
            self,
            self.frame,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            **kwargs
        )
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.grid(row=1, column=1, sticky="nsew")
        for sequence in ("<FocusIn>", "<FocusOut>", "<Enter>", "<Leave>", "<ButtonPress-1>", "<ButtonRelease-1>"):
            self.bind(sequence, self.__on_change_state, "+")
            self.bind(sequence, self.__on_update_stateful_style, "+")
            self.frame.bind(sequence, self.__on_update_stateful_style, "+")
        self.bind("<<ThemeChanged>>", self.__on_theme_changed, "+")
        self.bind("<<ThemeChanged>>", self.__on_update_stateful_style, "+")
        self.__specified_options = set()
        self._update_specified_options(kwargs)
        self.__style = Style(self)
        self._update_style()
        self.__copy_geometry_methods()

    def configure(self, cnf: Dict[str, Any] = None, **kwargs):
        super().configure(cnf, **kwargs)
        if cnf is not None:
            self._update_specified_options(cnf)
        self._update_specified_options(kwargs)

    config = configure

    def _update_specified_options(self, options: Dict[str, Any]):
        non_null_keys = {k for k, v in options.items() if v is not None}
        specified_options = _DYNAMIC_OPTIONS_TEXT & non_null_keys
        self.__specified_options = self.__specified_options | specified_options

    def _update_style(self):
        super().configure(
            selectbackground=self.__lookup_without_specified("selectbackground", None, ["focus"]),
            selectforeground=self.__lookup_without_specified("selectforeground", None, ["focus"]),
            insertwidth=self.__lookup_without_specified("insertwidth", None, ["focus"], 1),
            font=self.__lookup_without_specified("font", None, None, "TkDefaultFont"),
        )
        self.frame.configure(
            padding=self.__lookup_without_specified(None, "padding", None, 1),
            borderwidth=self.__lookup_without_specified(None, "borderwidth", None, 1),
        )
        text_padding = parse_padding(self.__lookup_without_specified(None, "textpadding", None, 0))
        super().grid_configure(padx=text_padding.to_padx(), pady=text_padding.to_pady())

    def _update_stateful_style(self, state):
        super().configure(
            background=self.__lookup_without_specified("background", "fieldbackground", state),
            foreground=self.__lookup_without_specified("foreground", None, state),
        )

    def __on_change_state(self, event: Event):
        # Older versions of Python do not support the `match` statement.
        if event.type == EventType.FocusIn:
            self.frame.state(["focus"])
        elif event.type == EventType.FocusOut:
            self.frame.state(["!focus"])
        elif event.type == EventType.Enter:
            self.frame.state(["hover"])
        elif event.type == EventType.Leave:
            self.frame.state(["!hover"])
        elif event.type == EventType.ButtonPress:
            if event.num == 1:
                self.frame.state(["pressed"])
        elif event.type == EventType.ButtonRelease:
            if event.num == 1:
                self.frame.state(["!pressed"])

    def __on_update_stateful_style(self, _: Event):
        self._update_stateful_style(self.frame.state())

    def __on_theme_changed(self, _: Event):
        self._update_style()

    def __lookup_without_specified(self, option: str = None, style_option: str = None, state=None, default=None):
        if option is None or option not in self.__specified_options:
            style_option = style_option if style_option is not None else option
            result = self.__style.lookup(self.frame.cget("style"), style_option, state, default)
            if result == "":
                return default
            return result
        return None

    def __copy_geometry_methods(self):
        """
        Copy geometry methods of self.frame without overriding Text methods.
        """

        for m in (vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()).difference(vars(Text).keys()):
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


def example():
    from tkinter import Tk

    root = Tk()
    root.geometry("300x300")
    root.title("ThemedText")
    text = ThemedText(root)
    text.pack(fill="both", expand=True, padx="7p", pady="7p")
    text.insert("1.0", "Hello, ThemedText!")
    root.mainloop()


if __name__ == "__main__":
    example()
