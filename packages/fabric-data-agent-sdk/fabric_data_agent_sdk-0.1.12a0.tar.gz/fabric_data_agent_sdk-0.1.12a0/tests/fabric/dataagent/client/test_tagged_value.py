import pytest
from unittest.mock import patch, MagicMock
import requests
from sempy.fabric.exceptions import FabricHTTPException

from fabric.dataagent.client._tagged_value import TaggedValue


class TestTaggedValue:
    """Tests for the TaggedValue class."""

    def test_init(self):
        """Test initialization of TaggedValue."""
        value = {"key": "value"}
        etag = "etag123"
        
        tv = TaggedValue(value, etag)
        
        assert tv.value == value
        assert tv.etag == etag

    def test_str(self):
        """Test __str__ method."""
        value = {"key": "value"}
        etag = "etag123"
        
        tv = TaggedValue(value, etag)
        
        expected_str = "{'key': 'value'} (ETag: etag123)"
        assert str(tv) == expected_str

    def test_repr(self):
        """Test __repr__ method."""
        value = {"key": "value"}
        etag = "etag123"
        
        tv = TaggedValue(value, etag)
        
        expected_repr = "TaggedValue(value={'key': 'value'}, etag=etag123)"
        assert repr(tv) == expected_repr

    def test_from_response_success(self):
        """Test from_response method with a successful response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_response.headers = {"ETag": "etag123"}
        
        result = TaggedValue.from_response(mock_response)
        
        assert isinstance(result, TaggedValue)
        assert result.value == {"key": "value"}
        assert result.etag == "etag123"

    def test_from_response_missing_etag(self):
        """Test from_response method with a missing ETag."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_response.headers = {}  # No ETag
        
        result = TaggedValue.from_response(mock_response)
        
        assert isinstance(result, TaggedValue)
        assert result.value == {"key": "value"}
        assert result.etag == ""  # Empty string when ETag is missing

    def test_from_response_error(self):
        """Test from_response method with an error response."""
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.url = "http://example.com"
        mock_response.headers = {}  # Ensure headers attribute exists
        
        with pytest.raises(FabricHTTPException):
            TaggedValue.from_response(mock_response)

    def test_value_modification(self):
        """Test that modifying the value works as expected."""
        value = {"key": "value"}
        etag = "etag123"
        
        tv = TaggedValue(value, etag)
        
        # Modify the value
        tv.value["key"] = "new_value"
        tv.value["new_key"] = "additional_value"
        
        assert tv.value == {"key": "new_value", "new_key": "additional_value"}
        assert tv.etag == etag  # ETag should remain unchanged

    def test_etag_modification(self):
        """Test that modifying the etag works as expected."""
        value = {"key": "value"}
        etag = "etag123"
        
        tv = TaggedValue(value, etag)
        
        # Modify the etag
        tv.etag = "new_etag456"
        
        assert tv.value == {"key": "value"}  # Value should remain unchanged
        assert tv.etag == "new_etag456"
