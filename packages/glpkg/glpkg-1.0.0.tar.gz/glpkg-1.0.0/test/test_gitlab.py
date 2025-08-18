import io
import pytest
import urllib
from gitlab.packages import *
from unittest.mock import mock_open, patch


class TestGitLab:
    @pytest.fixture
    def test_gitlab(self):
        return Packages("gl-host", "token-name", "token-value")

    def test_api_url(self, test_gitlab):
        assert test_gitlab.api_url() == "https://gl-host/api/v4/"

    def test_project_api_url(self, test_gitlab):
        assert (
            test_gitlab.project_api_url("24") == "https://gl-host/api/v4/projects/24/"
        )

    def test_get_headers(self, test_gitlab):
        assert test_gitlab.get_headers() == {"token-name": "token-value"}

    def test_get_headers_no_name(self):
        test_gitlab = Packages("gl-host", "", "token-value")
        assert test_gitlab.get_headers() == {}

    def test_get_headers_no_value(self):
        test_gitlab = Packages("gl-host", "token-name", "")
        assert test_gitlab.get_headers() == {}

    def test_get_headers_no_name_no_value(self):
        test_gitlab = Packages("gl-host", "", "")
        assert test_gitlab.get_headers() == {}

    def test_list_packages_none(self, test_gitlab):
        data = io.StringIO("[]")
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_packages("24", "package-name")
            assert len(packages) == 0

    def test_list_packages_one(self, test_gitlab):
        data = io.StringIO('[{"name": "package-name", "version": "0.1.2"}]')
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_packages("24", "package-name")
            assert len(packages) == 1

    def test_list_name_packages_filter(self, test_gitlab):
        data = io.StringIO(
            '[{"name": "package-name", "version": "0.1.2"}, {"name": "package-name-something", "version": "0.1.2"}]'
        )
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_packages("24", "package-name")
            assert len(packages) == 1

    def test_list_name_packages_five(self, test_gitlab):
        data = io.StringIO(
            '[{"name": "package-name", "version": "0.1"}, {"name": "package-name", "version": "0.2"}, {"name": "package-name", "version": "0.3"}, {"name": "package-name", "version": "0.4"}, {"name": "package-name", "version": "0.5"}]'
        )
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_packages("24", "package-name")
            assert len(packages) == 5

    def test_list_files_none(self, test_gitlab):
        data = io.StringIO("[]")
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_files("24", "123")
            assert len(packages) == 0

    def test_list_files_one(self, test_gitlab):
        data = io.StringIO('[{"file_name": "filea.txt"}]')
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_files("24", "123")
            assert len(packages) == 1

    def test_list_files_five(self, test_gitlab):
        data = io.StringIO(
            '[{"file_name": "filea.txt"}, {"file_name": "fileb.txt"}, {"file_name": "filec.txt"}, {"file_name": "filed.txt"}, {"file_name": "filee.txt"}]'
        )
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.list_files("24", "123")
            assert len(packages) == 5

    def test_package_id_none(self, test_gitlab):
        data = io.StringIO("[]")
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.get_package_id("24", "package-name", "0.1")
            assert packages == 0

    def test_package_id_one(self, test_gitlab):
        data = io.StringIO('[{"id": 123}]')
        with patch.object(urllib.request, "urlopen", return_value=data):
            packages = test_gitlab.get_package_id("24", "package-name", "0.1")
            assert packages == 123

    def test_upload_file(self, test_gitlab):
        class rmock:
            def getcode():
                return 201

        with patch("builtins.open", mock_open(read_data="data")):
            with patch.object(urllib.request, "urlopen", return_value=rmock):
                packages = test_gitlab.upload_file("24", "package-name", "0.1", "file")
                assert packages == 0

    def test_download_file(self, test_gitlab):
        data = io.StringIO("file-content")
        m = mock_open()
        with patch("builtins.open", mock_open()) as file_mock:
            # mock_open.write.return_value = 0
            with patch.object(urllib.request, "urlopen", return_value=data):
                test_gitlab.download_file("24", "package-name", "0.1", "file.txt")
                # assert ret == 0
            file_mock.assert_called_once_with("file.txt", "wb")
            file_mock().write.assert_called_once_with("file-content")
