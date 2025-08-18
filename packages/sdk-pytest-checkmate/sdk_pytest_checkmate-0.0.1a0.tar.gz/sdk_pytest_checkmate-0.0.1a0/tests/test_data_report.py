"""Tests for the add_data_report() functionality."""

import json
import time

from sdk_pytest_checkmate import add_data_report
from sdk_pytest_checkmate.plugin import DataRecord, _get_ctx


class TestAddDataReport:
    """Test the add_data_report() functionality."""

    def test_add_data_report_basic(self):
        """Test basic add_data_report usage."""
        test_data = {"key": "value", "number": 42}
        result = add_data_report(test_data, "Test Data")

        ctx = _get_ctx()
        data_reports = ctx["data_reports"]

        assert isinstance(result, DataRecord)
        assert len(data_reports) == 1

        record = data_reports[0]
        assert isinstance(record, DataRecord)
        assert record.label == "Test Data"
        assert record.payload == test_data
        assert record.seq == 0
        assert record.time > 0

    def test_add_data_report_different_types(self):
        """Test add_data_report with different data types."""
        # Dictionary
        dict_data = {"type": "dict", "items": [1, 2, 3]}
        add_data_report(dict_data, "Dictionary")

        # List
        list_data = [1, 2, 3, "string", {"nested": True}]
        add_data_report(list_data, "List")

        # String
        string_data = "Simple string data"
        add_data_report(string_data, "String")

        # Number
        number_data = 42.5
        add_data_report(number_data, "Number")

        # None
        none_data = None
        add_data_report(none_data, "None Value")

        # Custom object
        class CustomObject:
            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = 123

        custom_obj = CustomObject()
        add_data_report(custom_obj, "Custom Object")

        ctx = _get_ctx()
        data_reports = ctx["data_reports"]

        assert len(data_reports) == 6

        # Check all records have correct labels
        labels = [record.label for record in data_reports]
        assert "Dictionary" in labels
        assert "List" in labels
        assert "String" in labels
        assert "Number" in labels
        assert "None Value" in labels
        assert "Custom Object" in labels

        # Check payloads
        assert data_reports[0].payload == dict_data
        assert data_reports[1].payload == list_data
        assert data_reports[2].payload == string_data
        assert data_reports[3].payload == number_data
        assert data_reports[4].payload is None
        assert data_reports[5].payload == custom_obj

    def test_add_data_report_sequence(self):
        """Test multiple add_data_report calls maintain sequence."""
        add_data_report("First", "First Report")
        add_data_report("Second", "Second Report")
        add_data_report("Third", "Third Report")

        ctx = _get_ctx()
        data_reports = ctx["data_reports"]

        assert len(data_reports) == 3
        assert data_reports[0].seq == 0
        assert data_reports[1].seq == 1
        assert data_reports[2].seq == 2

        assert data_reports[0].label == "First Report"
        assert data_reports[1].label == "Second Report"
        assert data_reports[2].label == "Third Report"

    def test_add_data_report_timing(self):
        """Test that add_data_report records proper timing."""
        start_time = time.time()
        add_data_report("test", "Timing Test")
        end_time = time.time()

        ctx = _get_ctx()
        record = ctx["data_reports"][0]

        assert start_time <= record.time <= end_time

    def test_add_data_report_to_dict_serialization(self):
        """Test data record serialization to dictionary."""
        test_data = {"serialization": "test", "nested": {"value": 42}}
        add_data_report(test_data, "Serialization Test")

        ctx = _get_ctx()
        record = ctx["data_reports"][0]
        record_dict = record.to_dict()

        assert isinstance(record_dict, dict)
        assert record_dict["label"] == "Serialization Test"
        assert record_dict["seq"] == 0
        assert "time" in record_dict
        assert record_dict["time"] > 0
        assert record_dict["payload"] == test_data

    def test_add_data_report_json_serializable(self):
        """Test that typical data report payloads are JSON serializable."""
        # Test data types that should be JSON serializable
        json_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        add_data_report(json_data, "JSON Test")

        ctx = _get_ctx()
        record = ctx["data_reports"][0]

        # Should be able to serialize the payload
        serialized = json.dumps(record.payload)
        deserialized = json.loads(serialized)

        assert deserialized == json_data

    def test_add_data_report_large_data(self):
        """Test add_data_report with larger data structures."""
        # Create a larger data structure
        large_data = {
            "users": [
                {"id": i, "name": f"User {i}", "active": i % 2 == 0} for i in range(100)
            ],
            "metadata": {
                "total_count": 100,
                "generated_at": time.time(),
                "source": "test_suite",
            },
        }

        add_data_report(large_data, "Large Dataset")

        ctx = _get_ctx()
        record = ctx["data_reports"][0]

        assert record.label == "Large Dataset"
        assert len(record.payload["users"]) == 100
        assert record.payload["metadata"]["total_count"] == 100

    def test_add_data_report_return_value(self):
        """Test that add_data_report returns the DataRecord."""
        test_data = {"test": "return_value"}
        result = add_data_report(test_data, "Return Test")

        ctx = _get_ctx()
        stored_record = ctx["data_reports"][0]

        # The returned record should be the same as the stored one
        assert result is stored_record
        assert result.label == "Return Test"
        assert result.payload == test_data

    def test_add_data_report_empty_label(self):
        """Test add_data_report with empty label."""
        add_data_report("test_data", "")

        ctx = _get_ctx()
        record = ctx["data_reports"][0]

        assert record.label == ""
        assert record.payload == "test_data"
