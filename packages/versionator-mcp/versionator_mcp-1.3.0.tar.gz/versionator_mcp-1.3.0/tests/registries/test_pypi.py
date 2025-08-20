"""
Tests for PyPI registry functionality
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockResponse, MockSession
from tests.utils import get_pypi_version


class TestPyPIRegistry:
    """Test PyPI registry functionality"""

    @pytest.mark.asyncio
    async def test_get_pypi_version_success(self):
        """Test successful PyPI package version retrieval"""
        mock_response = MockResponse(
            200,
            json_data={
                "info": {
                    "name": "requests",
                    "version": "2.28.1",
                    "summary": "Python HTTP for Humans.",
                    "description": "Requests is a simple, yet elegant HTTP library.",
                    "home_page": "https://requests.readthedocs.io",
                    "author": "Kenneth Reitz",
                    "author_email": "me@kennethreitz.org",
                    "maintainer": "",
                    "maintainer_email": "",
                    "license": "Apache 2.0",
                    "keywords": "HTTP",
                    "platform": "UNKNOWN",
                    "classifiers": [],
                    "download_url": "",
                    "downloads": {"last_day": -1, "last_month": -1, "last_week": -1},
                    "package_url": "https://pypi.org/project/requests/",
                    "project_url": "https://pypi.org/project/requests/",
                    "project_urls": {
                        "Documentation": "https://requests.readthedocs.io",
                        "Source": "https://github.com/psf/requests",
                    },
                    "release_url": "https://pypi.org/project/requests/2.28.1/",
                    "requires_dist": [],
                    "requires_python": ">=3.7, <4",
                    "summary": "Python HTTP for Humans.",
                    "version": "2.28.1",
                    "yanked": False,
                    "yanked_reason": None,
                },
                "last_serial": 14517954,
                "releases": {
                    "2.28.1": [
                        {
                            "comment_text": "",
                            "digests": {
                                "md5": "f8c9ad6e5b4e0d1e2e3e4f5f6f7f8f9f",
                                "sha256": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
                            },
                            "downloads": -1,
                            "filename": "requests-2.28.1-py3-none-any.whl",
                            "has_sig": False,
                            "md5_digest": "f8c9ad6e5b4e0d1e2e3e4f5f6f7f8f9f",
                            "packagetype": "bdist_wheel",
                            "python_version": "py3",
                            "requires_python": ">=3.7, <4",
                            "size": 62317,
                            "upload_time": "2022-07-13T15:00:00",
                            "upload_time_iso_8601": "2022-07-13T15:00:00.000000Z",
                            "url": "https://files.pythonhosted.org/packages/ca/91/6d9b8ccacd0412c08820f72cebaa4f0a0e76c9b0e3317d6b1b1d2e3e4f5f6/requests-2.28.1-py3-none-any.whl",
                            "yanked": False,
                            "yanked_reason": None,
                        }
                    ]
                },
                "urls": [],
                "vulnerabilities": [],
            },
        )

        with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
            result = await get_pypi_version("requests")
            assert result.version == "2.28.1"
            assert result.registry == "pypi"
            assert "pypi.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_pypi_version_not_found(self):
        """Test PyPI package not found"""
        mock_response = MockResponse(404, text_data="Not found")

        with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
            with pytest.raises(Exception, match="Package 'nonexistent' not found in PyPI registry"):
                await get_pypi_version("nonexistent")
