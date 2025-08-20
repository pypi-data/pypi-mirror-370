"""Tests for the soft_assert() functionality."""

import time

from sdk_pytest_checkmate import soft_assert
from sdk_pytest_checkmate.plugin import SoftCheckRecord, _get_ctx


class TestSoftAssert:
    """Test the soft_assert() functionality."""

    def test_soft_assert_passing(self):
        """Test soft_assert with passing condition."""
        result = soft_assert(True, "This should pass")

        ctx = _get_ctx()
        soft_checks = ctx["soft_checks"]
        soft_failures = ctx["soft_failures"]

        assert result is True
        assert len(soft_checks) == 1
        assert len(soft_failures) == 0

        check_record = soft_checks[0]
        assert isinstance(check_record, SoftCheckRecord)
        assert check_record.message == "This should pass"
        assert check_record.passed is True
        assert check_record.seq == 0
        assert check_record.time > 0

    def test_soft_assert_failing(self):
        """Test soft_assert with failing condition."""
        result = soft_assert(False, "This should fail")

        ctx = _get_ctx()
        soft_checks = ctx["soft_checks"]
        soft_failures = ctx["soft_failures"]

        assert result is False
        assert len(soft_checks) == 1
        assert len(soft_failures) == 1
        assert soft_failures[0] == "This should fail"

        check_record = soft_checks[0]
        assert check_record.message == "This should fail"
        assert check_record.passed is False

    def test_soft_assert_default_message(self):
        """Test soft_assert with default message."""
        soft_assert(True)

        ctx = _get_ctx()
        check_record = ctx["soft_checks"][0]
        assert check_record.message == "Soft assertion"

    def test_soft_assert_sequence(self):
        """Test multiple soft_assert calls maintain sequence."""
        soft_assert(True, "First assertion")
        soft_assert(False, "Second assertion")
        soft_assert(True, "Third assertion")

        ctx = _get_ctx()
        soft_checks = ctx["soft_checks"]
        soft_failures = ctx["soft_failures"]

        assert len(soft_checks) == 3
        assert len(soft_failures) == 1
        assert soft_failures[0] == "Second assertion"

        assert soft_checks[0].seq == 0
        assert soft_checks[1].seq == 1
        assert soft_checks[2].seq == 2

        assert soft_checks[0].passed is True
        assert soft_checks[1].passed is False
        assert soft_checks[2].passed is True

    def test_soft_assert_mixed_types(self):
        """Test soft_assert with different condition types."""
        # Boolean
        soft_assert(True, "Boolean true")
        soft_assert(False, "Boolean false")

        # Truthy/falsy values converted to bool
        soft_assert(bool(1), "Truthy number")
        soft_assert(bool(0), "Falsy number")
        soft_assert(bool("hello"), "Non-empty string")
        soft_assert(bool(""), "Empty string")
        soft_assert(bool([1, 2, 3]), "Non-empty list")
        soft_assert(bool([]), "Empty list")

        ctx = _get_ctx()
        soft_checks = ctx["soft_checks"]
        soft_failures = ctx["soft_failures"]

        assert len(soft_checks) == 8
        assert len(soft_failures) == 4  # False, 0, "", []

        # Check which ones passed
        passed_messages = [check.message for check in soft_checks if check.passed]
        failed_messages = [check.message for check in soft_checks if not check.passed]

        assert "Boolean true" in passed_messages
        assert "Truthy number" in passed_messages
        assert "Non-empty string" in passed_messages
        assert "Non-empty list" in passed_messages

        assert "Boolean false" in failed_messages
        assert "Falsy number" in failed_messages
        assert "Empty string" in failed_messages
        assert "Empty list" in failed_messages

    def test_soft_assert_fluent_usage(self):
        """Test soft_assert can be used in fluent style."""
        # Test chaining with and/or
        result1 = soft_assert(True, "First") and soft_assert(True, "Second")
        result2 = soft_assert(False, "Third") or soft_assert(True, "Fourth")

        assert result1 is True
        assert result2 is True

        ctx = _get_ctx()
        assert len(ctx["soft_checks"]) == 4
        assert len(ctx["soft_failures"]) == 1

    def test_soft_assert_to_dict_serialization(self):
        """Test soft check record serialization to dictionary."""
        soft_assert(False, "Serialization test")

        ctx = _get_ctx()
        check_record = ctx["soft_checks"][0]
        check_dict = check_record.to_dict()

        assert isinstance(check_dict, dict)
        assert check_dict["message"] == "Serialization test"
        assert check_dict["passed"] is False
        assert check_dict["seq"] == 0
        assert "time" in check_dict
        assert check_dict["time"] > 0

    def test_soft_assert_timing(self):
        """Test that soft_assert records proper timing."""
        start_time = time.time()
        soft_assert(True, "Timing test")
        end_time = time.time()

        ctx = _get_ctx()
        check_record = ctx["soft_checks"][0]

        assert start_time <= check_record.time <= end_time

    def test_soft_assert_outside_test_context(self):
        """Test soft_assert behavior outside test context."""
        # This test can't easily be run outside pytest context
        # but we can verify the error would be raised
        pass  # Skip for now as it requires special setup
