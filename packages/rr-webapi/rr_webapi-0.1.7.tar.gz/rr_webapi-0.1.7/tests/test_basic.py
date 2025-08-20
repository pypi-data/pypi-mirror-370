"""
Basic tests for RaceResult Web API Python Library
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to allow importing rr_webapi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_import_main_api():
    """Test that the main API class can be imported"""
    try:
        from rr_webapi import API
        assert API is not None
    except ImportError as e:
        pytest.fail(f"Failed to import API: {e}")

def test_import_endpoints():
    """Test that endpoint modules can be imported"""
    try:
        from rr_webapi.endpoints import data, participants, contests, rawdata
        assert data is not None
        assert participants is not None
        assert contests is not None
        assert rawdata is not None
    except ImportError as e:
        pytest.fail(f"Failed to import endpoints: {e}")

def test_import_public_api():
    """Test that public API can be imported"""
    try:
        from rr_webapi.public import PublicAPI
        assert PublicAPI is not None
    except ImportError as e:
        pytest.fail(f"Failed to import PublicAPI: {e}")

def test_import_event_api():
    """Test that event API can be imported"""
    try:
        from rr_webapi.eventapi import EventAPI
        assert EventAPI is not None
    except ImportError as e:
        pytest.fail(f"Failed to import EventAPI: {e}")

def test_api_instantiation():
    """Test that API can be instantiated"""
    try:
        from rr_webapi import API
        api = API("test.server.com")
        assert api is not None
        assert hasattr(api, 'public')
        assert hasattr(api, 'event_api')
    except Exception as e:
        pytest.fail(f"Failed to instantiate API: {e}")

if __name__ == "__main__":
    pytest.main([__file__]) 