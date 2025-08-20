"""
Tests for HTTP client functionality
"""

import pytest

from tests.utils import set_request_timeout


def test_set_request_timeout():
    """Test setting request timeout"""
    set_request_timeout(60)
    # Test passes if no exception is raised
