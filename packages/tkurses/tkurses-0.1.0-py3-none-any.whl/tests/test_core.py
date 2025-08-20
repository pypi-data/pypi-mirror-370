import pytest
from cursesui.core import App, Widget

class DummyWidget(Widget):
    def __init__(self):
        super().__init__(0, 0)
        self.rendered = False
        self.handled_keys = []

    def render(self):
        self.rendered = True

    def handle_input(self, key):
        self.handled_keys.append(key)
        return key == 42  # handle only key 42

def test_add_widget_and_focus(mocker):
    mock_stdscr = mocker.MagicMock()
    app = App(mock_stdscr)
    w1 = DummyWidget()
    w2 = DummyWidget()
    app.add_widget(w1)
    app.add_widget(w2)

    assert w1.rendered
    assert w2.rendered
    assert app.focus_index == 0

    # Test focus cycling on Tab (key 9)
    app.handle_input(41)  # unhandled key
    assert app.focus_index == 0
    app.handle_input(9)   # Tab key
    assert app.focus_index == 1

def test_handle_input_handled_key(mocker):
    mock_stdscr = mocker.MagicMock()
    app = App(mock_stdscr)
    w = DummyWidget()
    app.add_widget(w)

    app.handle_input(42)  # handled by DummyWidget
    assert 42 in w.handled_keys
