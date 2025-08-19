from unittest.mock import MagicMock

import pytest
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication, QMainWindow, QWidget

from iblqt import tools


class TestGetApp:
    def test_get_app_returns_qapplication(self, qtbot):
        """Test that get_app returns the QApplication instance when one exists."""
        app = QApplication.instance()
        assert isinstance(app, QApplication)
        assert tools.get_app() is app


class TestGetOrCreateApp:
    def test_returns_qapplication_instance(self, qtbot, monkeypatch):
        monkeypatch.setattr(
            tools, 'get_app', lambda: (_ for _ in ()).throw(RuntimeError())
        )
        fake_app = MagicMock(spec=QApplication)
        monkeypatch.setattr(tools, 'QApplication', lambda argv: fake_app)
        app = tools.get_or_create_app()
        assert isinstance(app, QApplication)

    def test_returns_same_instance_on_multiple_calls(self, qtbot):
        app1 = tools.get_or_create_app([])
        app2 = tools.get_or_create_app([])
        assert app1 is app2


class TestRequireQtDecorator:
    @staticmethod
    @tools.require_qt
    def func():
        return 42

    def test_runs_function_when_qt_running(self, qtbot):
        assert self.func() == 42  # qtbot ensures QApplication is running

    def test_raises_runtime_error_when_no_qt(self, monkeypatch):
        monkeypatch.setattr('qtpy.QtWidgets.QApplication.instance', lambda: None)
        with pytest.raises(RuntimeError, match='requires a running QApplication.'):
            self.func()


class TestGetMainWindow:
    def test_returns_main_window_instance(self, qtbot):
        main_win = QMainWindow()
        main_win.show()
        qtbot.addWidget(main_win)

        assert tools.get_main_window() is main_win

    def test_raises_if_no_main_window_found(self, qtbot):
        widget = QWidget()
        widget.show()
        qtbot.addWidget(widget)

        with pytest.raises(RuntimeError, match='No QMainWindow instance found'):
            tools.get_main_window()


def test_run_as_qt_app(qtbot, monkeypatch):
    @tools.run_as_qt_app
    def create_widget():
        return QWidget()

    monkeypatch.setattr(QWidget, 'show', lambda self: None)

    app = QApplication.instance()
    QTimer.singleShot(100, app.quit)
    exit_code = create_widget()
    assert exit_code == 0
