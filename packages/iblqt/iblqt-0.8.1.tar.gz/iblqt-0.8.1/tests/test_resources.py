import importlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from qtpy.QtGui import QIcon

resources_path = Path(__file__).parents[1].joinpath('resources')


class TestResources:
    def test_rcc1(self):
        """Test Resources (version 1)."""
        with (
            patch('iblqt.resources.QtCore.qVersion', return_value='5.7.0'),
            patch('iblqt.resources.QtCore.qRegisterResourceData') as mock_register,
            patch('iblqt.resources.QtCore.qUnregisterResourceData') as mock_unregister,
        ):
            if 'iblqt.resources' in sys.modules:
                del sys.modules['iblqt.resources']
            resources = importlib.import_module('iblqt.resources')
            assert resources.rcc_version == 1
            assert resources.qt_resource_struct is resources.qt_resource_struct_v1
            mock_register.assert_called_once()
            resources.qCleanupResources()
            mock_unregister.assert_called_once()

    def test_rcc2(self):
        """Test Resources (version 2)."""
        with (
            patch('iblqt.resources.QtCore.qVersion', return_value='5.8.0'),
            patch('iblqt.resources.QtCore.qRegisterResourceData') as mock_register,
            patch('iblqt.resources.QtCore.qUnregisterResourceData') as mock_unregister,
        ):
            if 'iblqt.resources' in sys.modules:
                del sys.modules['iblqt.resources']
            resources = importlib.import_module('iblqt.resources')
            assert resources.rcc_version == 2
            assert resources.qt_resource_struct is resources.qt_resource_struct_v2
            mock_register.assert_called_once()
            resources.qCleanupResources()
            mock_unregister.assert_called_once()

    def test_resources(self, qtbot):
        if 'iblqt.resources' in sys.modules:
            del sys.modules['iblqt.resources']
        importlib.import_module('iblqt.resources')
        qrc_file = resources_path.joinpath('resources.qrc')
        assert qrc_file.exists()
        tree = ET.parse(qrc_file)
        root = tree.getroot()
        resource_names = []
        for resource in root.findall('qresource'):
            prefix = resource.get('prefix')
            for file in resource.findall('file'):
                resource_path = resources_path.joinpath(file.text)
                alias = file.get('alias')
                assert resource_path.exists()
                resource_name = f':/{prefix}/{alias or resource_path.stem}'
                icon = QIcon(resource_name)
                assert len(icon.availableSizes()) > 0
                resource_names.append(resource_name)
        expected_resources = [':/icon/check']
        for expected_resource in expected_resources:
            assert expected_resource in resource_names
