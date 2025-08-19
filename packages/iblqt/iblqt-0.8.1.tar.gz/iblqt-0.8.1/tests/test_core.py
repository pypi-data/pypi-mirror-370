import os
import sys
import time
from pathlib import Path
from unittest.mock import PropertyMock, patch

import numpy as np
import pandas as pd
import pytest
from qtpy import API_NAME as QT_VERSION
from qtpy.QtCore import QModelIndex, Qt, QThreadPool, QUrl
from requests import HTTPError

from iblqt import core


class TestDataFrameTableModel:
    @pytest.fixture
    def data_frame(self):
        yield pd.DataFrame({'X': [0, 1, 2], 'Y': ['A', 'B', 'C']})

    @pytest.fixture
    def model(self, data_frame, qtbot):
        yield core.ColoredDataFrameTableModel(dataFrame=data_frame)

    def test_instantiation(self, qtbot, data_frame):
        model = core.ColoredDataFrameTableModel()
        assert model.dataFrame.empty
        model = core.ColoredDataFrameTableModel(dataFrame=data_frame)
        assert model.dataFrame is not data_frame
        assert model.dataFrame.equals(data_frame)
        with qtbot.waitSignal(model.modelReset, timeout=100):
            model.dataFrame = data_frame

    def test_header_data(self, qtbot, model):
        assert model.headerData(-1, Qt.Orientation.Horizontal) is None
        assert model.headerData(1, Qt.Orientation.Horizontal) == 'Y'
        assert model.headerData(2, Qt.Orientation.Horizontal) is None
        assert model.headerData(-1, Qt.Orientation.Vertical) is None
        assert model.headerData(2, Qt.Orientation.Vertical) == 2
        assert model.headerData(3, Qt.Orientation.Vertical) is None
        assert model.headerData(0, 3) is None

    def test_index(self, qtbot, model):
        assert model.index(1, 0).row() == 1
        assert model.index(1, 0).column() == 0
        assert model.index(1, 0).isValid()
        assert not model.index(5, 5).isValid()
        assert model.index(5, 5) == QModelIndex()

    def test_write_read(self, qtbot, model):
        with qtbot.waitSignal(model.dataChanged, timeout=100):
            assert model.setData(model.index(0, 0), -1)
        assert model.dataFrame.iloc[0, 0] == -1
        assert model.setData(model.index(2, 0), np.nan)
        assert not model.setData(model.index(5, 5), 9)
        assert not model.setData(model.index(0, 0), 9, 6)
        assert model.data(model.index(0, 1)) == 'A'
        assert model.data(model.index(5, 5)) is None
        assert model.data(model.index(0, 1), 6) is None
        assert np.isnan(model.data(model.index(2, 0)))
        assert not isinstance(model.data(model.index(0, 2)), np.generic)

    def test_sort(self, qtbot, model):
        with qtbot.waitSignal(model.layoutChanged, timeout=100):
            model.sort(1, Qt.SortOrder.DescendingOrder)
        assert model.data(model.index(0, 1)) == 'C'
        assert model.setData(model.index(0, 1), 'D')
        assert model.data(model.index(0, 1)) == 'D'
        assert model.headerData(0, Qt.Orientation.Vertical) == 2
        with qtbot.waitSignal(model.layoutChanged, timeout=100):
            model.sort(1, Qt.SortOrder.AscendingOrder)
        assert model.data(model.index(0, 1)) == 'A'
        assert model.data(model.index(2, 1)) == 'D'
        assert model.headerData(0, Qt.Orientation.Vertical) == 0
        model.setDataFrame(pd.DataFrame())
        with qtbot.assertNotEmitted(model.layoutChanged):
            model.sort(1, Qt.SortOrder.AscendingOrder)
            model.sort(1, Qt.SortOrder.DescendingOrder)

    def test_colormap(self, qtbot, caplog, model):
        with qtbot.waitSignal(model.colormapChanged, timeout=100):
            model.colormap = 'CET-L1'
        assert model.getColormap() == 'CET-L1'
        model.sort(1, Qt.SortOrder.AscendingOrder)
        assert (
            model.data(model.index(0, 0), Qt.ItemDataRole.BackgroundRole).redF() == 0.0
        )
        assert (
            model.data(model.index(2, 0), Qt.ItemDataRole.BackgroundRole).redF() == 1.0
        )
        assert (
            model.data(model.index(0, 0), Qt.ItemDataRole.ForegroundRole).redF() == 1.0
        )
        assert (
            model.data(model.index(2, 0), Qt.ItemDataRole.ForegroundRole).redF() == 0.0
        )
        caplog.clear()
        model.setColormap('non-existant')
        assert caplog.records[0].levelname == 'WARNING'

    def test_alpha(self, qtbot, model):
        with qtbot.waitSignal(model.alphaChanged, timeout=100):
            model.alpha = 128
        assert model.alpha == 128
        assert (
            model.data(model.index(0, 0), Qt.ItemDataRole.BackgroundRole).alpha() == 128
        )
        assert (
            model.data(model.index(2, 0), Qt.ItemDataRole.BackgroundRole).alpha() == 128
        )

    def test_counts(self, qtbot, model):
        assert model.rowCount() == 3
        assert model.columnCount() == 2
        parent_index = model.createIndex(0, 0)
        assert model.rowCount(parent_index) == 0
        assert model.columnCount(parent_index) == 0


class TestPathWatcher:
    @pytest.fixture
    def path_watcher(self, qtbot):
        parent = core.QObject()
        watcher = core.PathWatcher(parent=parent, paths=[])
        yield watcher
        watcher.removePaths(watcher.directories())
        watcher.removePaths(watcher.files())

    def test_empty(self, qtbot, path_watcher):
        assert path_watcher.files() == []
        assert path_watcher.directories() == []

    def test_add_path(self, qtbot, path_watcher, tmp_path):
        file_path = Path(tmp_path).joinpath('watched_file.txt')
        assert path_watcher.addPath(file_path) is False
        file_path.touch()
        assert path_watcher.addPath(file_path) is True
        assert path_watcher.addPath(file_path) is False
        assert file_path in path_watcher.files()
        assert path_watcher.directories() == []

    def test_add_paths(self, qtbot, path_watcher, tmp_path):
        file_path = Path(tmp_path).joinpath('watched_file.txt')
        assert path_watcher.addPaths([file_path]) == [file_path]
        file_path.touch()
        assert path_watcher.addPaths([file_path]) == []
        assert path_watcher.addPaths([file_path]) == [file_path]
        assert file_path in path_watcher.files()
        assert path_watcher.directories() == []

    def test_remove_path(self, qtbot, path_watcher, tmp_path):
        assert path_watcher.removePath(tmp_path) is False
        assert path_watcher.addPath(tmp_path) is True
        assert tmp_path in path_watcher.directories()
        assert tmp_path not in path_watcher.files()
        assert path_watcher.removePath(tmp_path) is True
        assert path_watcher.removePath(tmp_path) is False
        assert tmp_path not in path_watcher.directories()

    def test_remove_paths(self, qtbot, path_watcher, tmp_path):
        assert path_watcher.removePaths([tmp_path]) == [tmp_path]
        assert path_watcher.addPaths([tmp_path]) == []
        assert tmp_path in path_watcher.directories()
        assert tmp_path not in path_watcher.files()
        assert path_watcher.removePaths([tmp_path]) == []
        assert path_watcher.removePaths([tmp_path]) == [tmp_path]
        assert tmp_path not in path_watcher.directories()

    def file_changed(self, qtbot, path_watcher, tmp_path):
        file_path = Path(tmp_path).joinpath('watched_file.txt')
        file_path.touch()
        path_watcher.addPath(file_path)
        with qtbot.waitSignal(path_watcher.fileChanged):
            with file_path.open('w') as f:
                f.write('Hello, World!')
                f.flush()
                os.fsync(f.fileno())

    def directory_changed(self, qtbot, path_watcher, tmp_path):
        file_path = Path(tmp_path).joinpath('watched_file.txt')
        file_path.touch()
        path_watcher.addPath(tmp_path)
        with qtbot.waitSignal(path_watcher.directoryChanged):
            with file_path.open('w') as f:
                f.write('Hello, World!')
                f.flush()
                os.fsync(f.fileno())


class TestQAlyx:
    @pytest.fixture
    def mock_client(self):
        """Mock the AlyxClient to avoid real network calls."""
        with patch('iblqt.core.AlyxClient', autospec=True) as MockAlyxClient:
            yield MockAlyxClient.return_value

    def test_client(self, qtbot, mock_client):
        q_alyx = core.QAlyx(base_url='https://example.com')
        assert q_alyx.client is mock_client

    def test_login_success(self, qtbot, mock_client):
        """Test successful login."""
        mock_client.user = 'test_user'
        type(mock_client).is_logged_in = PropertyMock(side_effect=[True, False, True])

        q_alyx = core.QAlyx(base_url='https://example.com')

        # user already logged in
        with qtbot.assertNotEmitted(q_alyx.loggedIn):
            q_alyx.login(username='test_user', password='correct_password')

        # user not yet logged in
        with (
            qtbot.waitSignal(q_alyx.loggedIn) as s1,
            qtbot.waitSignal(q_alyx.statusChanged) as s2,
        ):
            q_alyx.login(username='test_user', password='correct_password')
            assert s1.args[0] == 'test_user'
            assert s2.args[0] is True

    def test_login_failure(self, qtbot, mock_client):
        """Test login failure."""
        mock_client.base_url = 'https://example.com'
        mock_client.user = 'test_user'
        mock_client.is_logged_in = False

        q_alyx = core.QAlyx(base_url='https://example.com')

        mock_client.authenticate.side_effect = UserWarning(
            'No password or cached token'
        )
        with qtbot.waitSignal(q_alyx.tokenMissing) as s1:
            q_alyx.login(username='test_user', password='some_password')
            assert s1.args[0] == 'test_user'

        mock_client.authenticate.side_effect = ConnectionError("Can't connect")
        with (
            qtbot.waitSignal(q_alyx.connectionFailed),
            patch('iblqt.core.QMessageBox.critical') as mock,
        ):
            q_alyx.login(username='test_user', password='some_password')
            mock.assert_called_once()

        mock_client.authenticate.side_effect = HTTPError(400, 'Blah')
        with qtbot.waitSignal(q_alyx.authenticationFailed) as s1:
            q_alyx.login(username='test_user', password='some_password')
            assert s1.args[0] == 'test_user'

        mock_client.authenticate.side_effect = HTTPError(401, 'Blah')
        with pytest.raises(HTTPError):
            q_alyx.login(username='test_user', password='some_password')

    def test_logout(self, qtbot, mock_client):
        """Test logout functionality."""
        q_alyx = core.QAlyx(base_url='https://example.com')

        mock_client.is_logged_in = False
        with qtbot.assertNotEmitted(q_alyx.loggedOut):
            q_alyx.logout()

        mock_client.is_logged_in = True
        with (
            qtbot.waitSignal(q_alyx.statusChanged) as s1,
            qtbot.waitSignal(q_alyx.loggedOut),
        ):
            q_alyx.logout()
            assert s1.args[0] is False

    def test_rest(self, qtbot, mock_client):
        """Test rest functionality."""
        q_alyx = core.QAlyx(base_url='https://example.com')
        q_alyx.rest('some_arg', some_kwarg=True)
        mock_client.rest.assert_called_once_with('some_arg', some_kwarg=True)

        mock_client.rest.side_effect = HTTPError(400, 'Blah')
        with patch('iblqt.core.QMessageBox.critical') as mock:
            q_alyx.rest('some_arg', some_kwarg=True)
            mock.assert_called_once()

        mock_client.rest.side_effect = HTTPError(401, 'Blah')
        with (
            qtbot.waitSignal(q_alyx.connectionFailed),
            patch('iblqt.core.QMessageBox.critical') as mock,
        ):
            q_alyx.rest('some_arg', some_kwarg=True)
            mock.assert_called_once()

    def test_connection_failed(self, qtbot, mock_client):
        mock_client.user = 'test_user'
        q_alyx = core.QAlyx(base_url='https://example.com')
        with qtbot.waitSignal(q_alyx.authenticationFailed) as s:
            q_alyx._onConnectionFailed(HTTPError(400, 'Blah'))
            assert s.args == ['test_user']
        with pytest.raises(ValueError):
            q_alyx._onConnectionFailed(ValueError('test'))


class TestWorker:
    def test_success_signal_threaded(self, qtbot):
        """Threaded: result and finished signals emitted on success."""

        def successful_task(x, y):
            return x + y

        worker = core.Worker(successful_task, 2, 3)

        with (
            qtbot.waitSignal(worker.signals.result, timeout=1000) as result_signal,
            qtbot.waitSignal(worker.signals.finished, timeout=1000),
        ):
            QThreadPool.globalInstance().start(worker)

        assert result_signal.args == [5]

    def test_error_signal_threaded(self, qtbot):
        """Threaded: error and finished signals emitted on failure."""

        def failing_task():
            raise ValueError('Intentional failure')

        worker = core.Worker(failing_task)

        with (
            qtbot.waitSignal(worker.signals.error, timeout=1000) as error_signal,
            qtbot.waitSignal(worker.signals.finished, timeout=1000),
        ):
            QThreadPool.globalInstance().start(worker)

        exctype, value, tb_str = error_signal.args[0]
        assert exctype is ValueError
        assert str(value) == 'Intentional failure'
        assert 'ValueError' in tb_str

    def test_progress_signal_threaded(self, qtbot):
        """Threaded: emits progress signals during execution."""

        def task_with_progress(progress_callback):
            for i in range(3):
                time.sleep(0.05)
                progress_callback.emit(i * 25)
            return 'done'

        worker = core.Worker(task_with_progress)
        progress_values = []
        worker.signals.progress.connect(progress_values.append)

        with (
            qtbot.waitSignal(worker.signals.result, timeout=2000) as result_signal,
            qtbot.waitSignal(worker.signals.finished, timeout=1000),
        ):
            QThreadPool.globalInstance().start(worker)

        assert result_signal.args == ['done']
        assert progress_values == [0, 25, 50]

    def test_worker_run_success_direct(self, qtbot):
        """Direct: run() emits correct signals on success."""

        def task(x):
            return x * 2

        worker = core.Worker(task, 21)

        result_emitted = []
        finished_emitted = []

        worker.signals.result.connect(result_emitted.append)
        worker.signals.finished.connect(lambda: finished_emitted.append(True))

        worker.run()

        assert result_emitted == [42]
        assert finished_emitted == [True]

    def test_worker_run_error_direct(self, qtbot):
        """Direct: run() emits error and finished signals on exception."""

        def failing():
            raise RuntimeError('failure')

        worker = core.Worker(failing)

        error_emitted = []
        finished_emitted = []

        worker.signals.error.connect(error_emitted.append)
        worker.signals.finished.connect(lambda: finished_emitted.append(True))

        worker.run()

        assert len(error_emitted) == 1
        exctype, value, tb_str = error_emitted[0]
        assert exctype is RuntimeError
        assert str(value) == 'failure'
        assert 'RuntimeError' in tb_str
        assert finished_emitted == [True]

    def test_worker_signals_attributes(self):
        """Test that WorkerSignals defines the correct signal attributes."""
        signals = core.WorkerSignals()
        assert hasattr(signals, 'finished')
        assert hasattr(signals, 'error')
        assert hasattr(signals, 'result')
        assert hasattr(signals, 'progress')


@pytest.mark.skipif(
    sys.platform == 'win32' and QT_VERSION == 'PyQt5' and 'TOX' in os.environ,
    reason='Test fails when run in Tox with PyQt5 on Windows',
)  # TODO
class TestRestrictedWebEnginePage:
    @pytest.fixture
    def web_engine_page(self, qtbot):
        page = core.RestrictedWebEnginePage(trusted_url_prefix='http://localhost/local')
        yield page
        with qtbot.waitSignal(page.destroyed, timeout=100):
            page.deleteLater()

    def test_internal_url_allows_navigation(self, qtbot, web_engine_page):
        assert isinstance(web_engine_page, core.QWebEnginePage)
        result = web_engine_page.acceptNavigationRequest(
            url=QUrl('http://localhost/local/page'),
            navigationType=core.QWebEnginePage.NavigationType.NavigationTypeLinkClicked,
            is_main_frame=True,
        )
        assert result is True

    @patch('iblqt.core.webbrowser.open')
    def test_external_url_opens_in_browser(self, mock_open, qtbot, web_engine_page):
        result = web_engine_page.acceptNavigationRequest(
            url=QUrl('http://localhost/external/page'),
            navigationType=core.QWebEnginePage.NavigationType.NavigationTypeLinkClicked,
            is_main_frame=True,
        )
        mock_open.assert_called_once_with('http://localhost/external/page')
        assert result is False
