from typing import Any, NamedTuple, Optional, Tuple


class Padding(NamedTuple):
    left: Any
    top: Any
    right: Any
    bottom: Any

    def to_padx(self) -> Tuple[Any, Any]:
        return self.left, self.right

    def to_pady(self) -> Tuple[Any, Any]:
        return self.top, self.bottom


def parse_padding(padding) -> Optional[Padding]:
    if padding is None:
        return None
    elif isinstance(padding, int):
        return Padding(padding, padding, padding, padding)
    elif isinstance(padding, str):
        padding = tuple(padding.split())
    elif not isinstance(padding, tuple):
        raise TypeError(f"Invalid padding type: {type(padding)}")
    left, top, right, bottom, *_ = padding + (None, None, None)
    top = top if top is not None else left
    right = right if right is not None else left
    bottom = bottom if bottom is not None else top
    return Padding(left, top, right, bottom)
