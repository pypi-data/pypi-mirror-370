import os
import sys
from collections import namedtuple
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from qtpy import API_NAME as QT_VERSION
from qtpy.QtCore import Qt, QUrl
from qtpy.QtGui import QColor, QPainter, QPalette, QStandardItemModel
from qtpy.QtWebEngineWidgets import QWebEnginePage
from qtpy.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QStyle,
    QStyleOptionViewItem,
    QTableView,
)

from iblqt import widgets
from iblqt.core import QAlyx


class TestCheckBoxDelegate:
    @pytest.fixture
    def setup_method(self, qtbot):
        self.model = QStandardItemModel(5, 1)  # 5 rows, 1 column
        for row in range(5):
            self.model.setData(self.model.index(row, 0), False)

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        qtbot.addWidget(self.table_view)

        self.delegate = widgets.CheckBoxDelegate()
        self.table_view.setItemDelegate(self.delegate)

    def test_checkbox_initial_state(self, qtbot, setup_method):
        # Check the initial state of the checkboxes
        for row in range(5):
            index = self.model.index(row, 0)
            assert self.model.data(index) is False  # Initially, all should be False

    def test_checkbox_toggle(self, qtbot, setup_method):
        # Simulate a mouse click to toggle the checkbox
        index = self.model.index(0, 0)  # Get the first checkbox
        rect = self.table_view.visualRect(index)

        # Simulate a mouse click in the center of the checkbox
        qtbot.mouseClick(self.table_view.viewport(), Qt.LeftButton, pos=rect.center())
        assert self.model.data(index) is True

        # Simulate another click to toggle it back
        qtbot.mouseClick(self.table_view.viewport(), Qt.LeftButton, pos=rect.center())
        assert self.model.data(index) is False

    def test_painting_checkbox(self, qtbot, setup_method):
        # Create a QPainter to test the painting of the checkbox
        painter = QPainter(self.table_view.viewport())
        option = QStyleOptionViewItem()
        index = self.model.index(0, 0)

        option.rect = self.table_view.visualRect(index)
        option.state = QStyle.State_On if self.model.data(index) else QStyle.State_Off
        self.delegate.paint(painter, option, index)


class TestColoredButton:
    @pytest.fixture
    def button_factory(self, qtbot):
        def _create_button(text='Click Me', color=None, parent=None):
            button = widgets.ColoredButton(text, color=color, parent=parent)
            qtbot.addWidget(button)
            return button

        return _create_button

    def test_default_color(self, button_factory):
        button = button_factory()
        default_color = button._original_color
        assert button.color() == default_color

    def test_initial_color(self, button_factory):
        button = button_factory(color=QColor('red'))
        assert button.color() == QColor('red')

    def test_set_color(self, button_factory):
        button = button_factory()
        new_color = QColor('red')
        button.setColor(new_color)
        assert button.color() == new_color

    def test_resets_color(self, button_factory):
        button = button_factory()
        original = button._original_color
        button.setColor(QColor('blue'))
        button.setColor(None)
        assert button.color() == original


class TestStatefulButton:
    def test_initial_state(self, qtbot):
        """Test the initial state of the StatefulButton."""
        button = widgets.StatefulButton('Active', 'Inactive', active=False)
        qtbot.addWidget(button)

        assert button.active is False
        assert button.text() == 'Inactive'

    def test_click_inactive_state(self, qtbot):
        """Test clicking the button while inactive."""
        button = widgets.StatefulButton('Active', 'Inactive', active=False)
        qtbot.addWidget(button)
        assert button.text() == 'Inactive'

        with qtbot.waitSignal(button.clickedWhileInactive):
            qtbot.mouseClick(button, Qt.LeftButton)

        assert button.active is False
        assert button.text() == 'Inactive'

    def test_click_active_state(self, qtbot):
        """Test clicking the button while active."""
        button = widgets.StatefulButton('Active', 'Inactive', active=True)
        qtbot.addWidget(button)
        assert button.text() == 'Active'

        with qtbot.waitSignal(button.clickedWhileActive):
            qtbot.mouseClick(button, Qt.LeftButton)

        assert button.active is True
        assert button.text() == 'Active'

    def test_state_change(self, qtbot):
        """Test state change and text update."""
        button = widgets.StatefulButton('Active', 'Inactive', active=False)
        qtbot.addWidget(button)

        assert button.getTextActive() == 'Active'
        assert button.getTextInactive() == 'Inactive'

        with qtbot.waitSignal(button.stateChanged):
            button.setActive(True)
        with qtbot.assertNotEmitted(button.stateChanged):
            button.setActive(True)
        assert button.active is True
        assert button.text() == 'Active'
        button.setTextActive('Active New')
        assert button.getTextActive() == 'Active New'
        assert button.text() == 'Active New'

        with qtbot.waitSignal(button.stateChanged):
            button.setActive(False)
        with qtbot.assertNotEmitted(button.stateChanged):
            button.setActive(False)
        assert button.active is False
        assert button.text() == 'Inactive'
        button.setTextInactive('Inactive New')
        assert button.getTextInactive() == 'Inactive New'
        assert button.text() == 'Inactive New'


class TestAlyxUserEdit:
    @pytest.fixture
    def setup_method(self, qtbot):
        """Fixture to set up the AlyxUserEdit widget for testing."""
        self.alyx_mock = MagicMock()
        self.user_edit = widgets.AlyxUserEdit(alyx=self.alyx_mock, parent=None)
        qtbot.addWidget(self.user_edit)

    def test_without_username(self, qtbot, setup_method):
        """Test login attempt without username."""
        self.user_edit.setText('')
        qtbot.keyPress(self.user_edit, Qt.Key_Return)
        self.alyx_mock.login.assert_not_called()

    def test_login_success(self, qtbot, setup_method):
        """Test successful login."""
        self.user_edit.setText('test_user')
        qtbot.keyPress(self.user_edit, Qt.Key_Return)
        self.alyx_mock.login.assert_called_once_with(username='test_user')

    def test_on_logged_in(self, qtbot, setup_method):
        """Test UI updates on successful login."""
        assert self.user_edit.isReadOnly() is False
        self.user_edit._onLoggedIn('test_user')
        assert self.user_edit.text() == 'test_user'
        assert self.user_edit.isReadOnly() is True

    def test_on_logged_out(self, qtbot, setup_method):
        """Test UI resets on logout."""
        self.user_edit._onLoggedIn('test_user')
        assert self.user_edit.isReadOnly() is True
        self.user_edit._onLoggedOut()
        assert self.user_edit.text() == ''
        assert self.user_edit.isReadOnly() is False
        assert self.user_edit.styleSheet() == ''

    def test_on_token_missing(self, qtbot, setup_method):
        """Test prompting for password when token is missing."""
        with patch('iblqt.widgets.AlyxLoginDialog', autospec=True) as mock:
            self.user_edit._onTokenMissing('test_user')
            mock.assert_called_once()
            assert 'test_user' in mock.call_args[0]


class TestAlyxLoginWidget:
    @pytest.fixture
    def setup_method(self, qtbot):
        """Fixture to set up the AlyxLoginWidget for testing."""
        self.alyx_mock = MagicMock(spec=QAlyx)
        self.login_widget = widgets.AlyxLoginWidget(alyx=self.alyx_mock, parent=None)
        qtbot.addWidget(self.login_widget)

    def test_instantiation(self, qtbot):
        """Test instantiation."""
        alyx_mock = MagicMock(spec=QAlyx)
        login_widget = widgets.AlyxLoginWidget(alyx=alyx_mock, parent=None)
        qtbot.addWidget(login_widget)
        assert login_widget.alyx is alyx_mock

        with patch('iblqt.core.AlyxClient') as client_mock:
            login_widget = widgets.AlyxLoginWidget(
                alyx='https://example.com', parent=None
            )
            qtbot.addWidget(login_widget)
            client_mock.assert_called_once()
            assert 'https://example.com' in client_mock.call_args[1].values()

    def test_enable_login_button(self, qtbot, setup_method):
        """Test that the login button is enabled when a username is entered."""
        assert not self.login_widget.button.isEnabled()
        self.login_widget.userEdit.setText('test_user')
        assert self.login_widget.button.isEnabled()
        self.login_widget.userEdit.setText('')
        assert not self.login_widget.button.isEnabled()

    def test_login_action(self, qtbot, setup_method):
        """Test that the login action is triggered when the button is clicked."""
        assert self.login_widget.button.text() == 'Login'
        self.login_widget.userEdit.setText('test_user')
        with qtbot.waitSignal(self.login_widget.button.clickedWhileInactive):
            qtbot.mouseClick(self.login_widget.button, Qt.LeftButton)
        self.alyx_mock.login.assert_called_once_with(username='test_user')
        self.login_widget.button.setActive(True)
        assert self.login_widget.button.text() == 'Logout'

    def test_logout_action(self, qtbot, setup_method):
        """Test that the logout action is triggered when the button is clicked."""
        self.login_widget.userEdit.setText('test_user')
        with qtbot.waitSignal(self.login_widget.button.clickedWhileInactive):
            qtbot.mouseClick(self.login_widget.button, Qt.LeftButton)
        self.alyx_mock.login.assert_called_once_with(username='test_user')
        self.login_widget.button.setActive(True)

        assert self.login_widget.button.text() == 'Logout'
        with qtbot.waitSignal(self.login_widget.button.clickedWhileActive):
            qtbot.mouseClick(self.login_widget.button, Qt.LeftButton)
        self.alyx_mock.logout.assert_called_once()
        self.login_widget.button.setActive(False)
        assert self.login_widget.button.text() == 'Login'


class TestAlyxLoginDialog:
    @pytest.fixture
    def mock_q_alyx(self):
        """Mock the QAlyx instance."""
        mock = MagicMock(spec=QAlyx)
        mock.client.base_url = 'https://example.com'
        return mock

    @pytest.fixture
    def dialog(self, mock_q_alyx):
        """Create an instance of AlyxLoginDialog for testing."""
        return widgets.AlyxLoginDialog(mock_q_alyx)

    def test_initial_state(self, qtbot, dialog):
        """Test the initial state of the dialog."""
        qtbot.addWidget(dialog)
        assert dialog.userEdit.text() == ''
        assert dialog.passEdit.text() == ''
        assert not dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()

    def test_enable_ok_button_when_text_entered(self, qtbot, dialog):
        """Test that the OK button is enabled when both fields are filled."""
        qtbot.addWidget(dialog)
        dialog.userEdit.setText('test_user')
        dialog.passEdit.setText('test_password')
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()

    def test_authentication_success(self, dialog, qtbot):
        """Test the dialog behavior on successful authentication."""
        qtbot.addWidget(dialog)
        dialog.userEdit.setText('test_user')
        dialog.passEdit.setText('test_password')
        with qtbot.waitSignal(dialog.accepted):
            qtbot.mouseClick(
                dialog.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton
            )
            dialog._alyx.login.assert_called_once_with(
                'test_user', 'test_password', False
            )
            dialog._onAuthentificationSucceeded('test_user')
        assert dialog.result() == QDialog.Accepted

    def test_authentication_failure(self, dialog, qtbot):
        """Test the dialog behavior on failed authentication."""
        qtbot.addWidget(dialog)
        dialog.userEdit.setText('test_user')
        dialog.passEdit.setText('test_password')
        with patch('iblqt.widgets.QMessageBox.critical') as mock:
            qtbot.mouseClick(
                dialog.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton
            )
            dialog._alyx.login.assert_called_once_with(
                'test_user', 'test_password', False
            )
            dialog._onAuthentificationFailed('test_user')
            mock.assert_called_once()
        assert dialog.passEdit.text() == ''
        assert dialog.result() == QDialog.Rejected

    def test_cache_checkbox(self, qtbot, dialog, mock_q_alyx):
        """Test the behavior of the cache checkbox."""
        qtbot.addWidget(dialog)
        check_cache = dialog.findChild(QCheckBox)
        assert check_cache is not None
        assert not check_cache.isChecked()

        check_cache.setChecked(True)
        dialog._setCache(check_cache.checkState())
        assert dialog._cache is True

        check_cache.setChecked(False)
        dialog._setCache(check_cache.checkState())
        assert dialog._cache is False

        dialog2 = widgets.AlyxLoginDialog(
            mock_q_alyx, cache=widgets.UseTokenCache.ALWAYS
        )
        qtbot.addWidget(dialog2)
        assert dialog2._cache
        assert dialog2.findChild(QCheckBox) is None

        dialog3 = widgets.AlyxLoginDialog(
            mock_q_alyx, cache=widgets.UseTokenCache.NEVER
        )
        qtbot.addWidget(dialog3)
        assert not dialog3._cache
        assert dialog3.findChild(QCheckBox) is None


class TestThresholdProgressBar:
    def test_color_change(self, qtbot):
        bar = widgets.ThresholdProgressBar(
            50, QColor('orange'), QColor('green'), value=30
        )
        qtbot.addWidget(bar)
        assert bar.threshold() == 50

        assert bar.palette().color(QPalette.Highlight) == QColor('green')
        bar.setValue(60)
        assert bar.palette().color(QPalette.Highlight) == QColor('orange')
        bar.setValue(40)
        assert bar.palette().color(QPalette.Highlight) == QColor('green')
        bar.setThreshold(30)
        assert bar.palette().color(QPalette.Highlight) == QColor('orange')
        assert bar.threshold() == 30

    def test_signals(self, qtbot):
        bar = widgets.ThresholdProgressBar(threshold=50, value=40)
        qtbot.addWidget(bar)
        assert not bar.aboveThreshold()

        with qtbot.waitSignal(bar.thresholdCrossed, timeout=1000) as blocker:
            bar.setValue(60)
            assert blocker.args[0] is True
            assert bar.aboveThreshold()
        with qtbot.waitSignal(bar.thresholdCrossed, timeout=1000) as blocker:
            bar.setValue(40)
            assert blocker.args[0] is False
        with (
            qtbot.waitSignal(bar.thresholdCrossed, timeout=1000) as blocker1,
            qtbot.waitSignal(bar.thresholdChanged, timeout=1000) as blocker2,
        ):
            bar.setThreshold(30)
            assert blocker1.args[0] is True
            assert blocker2.args[0] == 30


_ntuple_diskusage = namedtuple('_ntuple_diskusage', ['total', 'used', 'free'])


class TestDiskSpaceIndicator:
    def test_initialization_and_display(self, qtbot, monkeypatch):
        dummy_data = _ntuple_diskusage(total=1000, used=500, free=500)
        monkeypatch.setattr('iblqt.widgets.disk_usage', lambda path: dummy_data)

        indicator = widgets.DiskSpaceIndicator(percent_threshold=90)
        qtbot.addWidget(indicator)
        indicator._on_result(dummy_data)

        assert indicator.value() == 50
        assert indicator.directory() == Path.cwd().anchor

    def test_threshold_cross_signal_emitted(self, qtbot, monkeypatch):
        dummy_data = _ntuple_diskusage(total=1000, used=950, free=50)
        monkeypatch.setattr('iblqt.widgets.disk_usage', lambda path: dummy_data)

        indicator = widgets.DiskSpaceIndicator(directory='/', percent_threshold=90)
        qtbot.addWidget(indicator)

        with qtbot.waitSignal(indicator.thresholdCrossed, timeout=1000) as blocker:
            indicator._on_result(dummy_data)
            assert blocker.args[0] is True


@pytest.mark.skipif(
    sys.platform == 'win32' and QT_VERSION == 'PyQt5' and 'TOX' in os.environ,
    reason='Test fails when run in Tox with PyQt5 on Windows',
)  # TODO
class TestRestrictedWebView:
    @pytest.fixture
    def browser_widget_factory(self, qtbot):
        created_widgets = []

        def _browser_widget(*args, **kwargs):
            widget = widgets.RestrictedWebView(*args, **kwargs)
            created_widgets.append(widget)
            qtbot.addWidget(widget)
            return widget

        yield _browser_widget

        for widget in created_widgets:
            try:
                page = widget.webEngineView.page()
            except RuntimeError:
                continue
            with qtbot.waitSignal(page.destroyed):
                widget.close()

    @pytest.fixture
    def browser_widget(self, qtbot, browser_widget_factory):
        yield browser_widget_factory(
            url=QUrl('http://localhost/trusted/start'),
            trusted_url_prefix='http://localhost/trusted/',
        )

    def test_default_prefix(self, qtbot):
        widget = widgets.RestrictedWebView(url='http://localhost/')
        qtbot.addWidget(widget)
        assert widget.trustedUrlPrefix() == 'http://localhost/'

    def test_initial_url_loaded(self, qtbot, browser_widget):
        assert browser_widget.url() == QUrl('http://localhost/trusted/start')
        assert browser_widget.trustedUrlPrefix() == 'http://localhost/trusted/'

    def test_get_set_url(self, qtbot, browser_widget):
        assert browser_widget.setUrl(QUrl('http://localhost/trusted/some_page'))
        assert browser_widget.url() == QUrl('http://localhost/trusted/some_page')
        assert browser_widget.setUrl('http://localhost/trusted/other')
        assert browser_widget.url() == QUrl('http://localhost/trusted/other')
        assert not browser_widget.setUrl('http://localhost/external/page')
        assert browser_widget.url() == QUrl('http://localhost/trusted/other')

    @pytest.mark.xfail(sys.platform == 'win32', reason='Tends to fail on Windows')
    def test_home_button_loads_home(self, qtbot, browser_widget):
        browser_widget.setUrl('http://localhost/trusted/other')
        with qtbot.waitSignal(browser_widget.webEngineView.urlChanged):
            qtbot.mouseClick(browser_widget.uiPushHome, Qt.MouseButton.LeftButton)
        assert browser_widget.url() == QUrl('http://localhost/trusted/start')

    @patch('iblqt.widgets.webbrowser.open')
    def test_open_in_browser_button(self, mock_open, qtbot, browser_widget):
        qtbot.mouseClick(browser_widget.uiPushBrowser, Qt.MouseButton.LeftButton)
        mock_open.assert_called_once_with('http://localhost/trusted/start')

    @patch('iblqt.widgets.webbrowser.open')
    def test_click_internal_link(self, mock_open, qtbot, browser_widget):
        result = browser_widget.webEnginePage.acceptNavigationRequest(
            url=QUrl('http://localhost/trusted/page'),
            navigationType=QWebEnginePage.NavigationType.NavigationTypeLinkClicked,
            is_main_frame=True,
        )
        assert result is True
        mock_open.assert_not_called()

    @patch('iblqt.widgets.webbrowser.open')
    def test_click_external_link(self, mock_open, qtbot, browser_widget):
        result = browser_widget.webEnginePage.acceptNavigationRequest(
            url=QUrl('http://localhost/external/page'),
            navigationType=QWebEnginePage.NavigationType.NavigationTypeLinkClicked,
            is_main_frame=True,
        )
        assert result is False
        mock_open.assert_called_once_with('http://localhost/external/page')

    @patch('iblqt.widgets.webbrowser.open')
    def test_change_prefix(self, mock_open, qtbot, browser_widget):
        browser_widget.setTrustedUrlPrefix('http://localhost/external')
        result = browser_widget.webEnginePage.acceptNavigationRequest(
            url=QUrl('http://localhost/external/page'),
            navigationType=QWebEnginePage.NavigationType.NavigationTypeLinkClicked,
            is_main_frame=True,
        )
        assert result is True
        mock_open.assert_not_called()

    def test_tool_and_status_tips(self, qtbot, browser_widget_factory):
        widget = browser_widget_factory('http://localhost/')
        assert len(widget.uiPushHome.toolTip()) > 0
        assert len(widget.uiPushHome.statusTip()) == 0
        widget = browser_widget_factory(
            'http://localhost/', use_tool_tips=False, use_status_tips=True
        )
        assert len(widget.uiPushHome.toolTip()) == 0
        assert len(widget.uiPushHome.statusTip()) > 0
        widget = browser_widget_factory(
            'http://localhost/', use_tool_tips=True, use_status_tips=False
        )
        assert len(widget.uiPushHome.toolTip()) > 0
        assert len(widget.uiPushHome.statusTip()) == 0


class TestSlideToggle:
    @pytest.fixture
    def slider(self, qtbot):
        widget = widgets.SlideToggle()
        qtbot.addWidget(widget)
        widget.show()
        qtbot.waitExposed(widget)
        return widget

    def test_initial_state(self, qtbot, slider):
        assert not slider.isChecked()
        assert slider.isEnabled() is True
        assert slider.isChecked() is False
        assert slider._relative_position == 0.0

    def test_toggle_changes_state(self, qtbot, slider):
        qtbot.mouseClick(slider, Qt.LeftButton)
        assert slider.isChecked() is True
        slider._animation.setCurrentTime(slider._animation.duration())
        assert slider._relative_position == 1.0

    def test_disabled_does_not_toggle(self, qtbot, slider):
        slider.setEnabled(False)
        qtbot.mouseClick(slider, Qt.LeftButton)
        assert slider.isChecked() is False

    def test_emits_toggled_signal(self, qtbot, slider):
        with qtbot.waitSignal(slider.toggled, timeout=500) as blocker:
            qtbot.mouseClick(slider, Qt.LeftButton)
        assert blocker.args == [True]
        with qtbot.waitSignal(slider.toggled, timeout=500) as blocker:
            qtbot.mouseClick(slider, Qt.LeftButton)
        assert blocker.args == [False]
