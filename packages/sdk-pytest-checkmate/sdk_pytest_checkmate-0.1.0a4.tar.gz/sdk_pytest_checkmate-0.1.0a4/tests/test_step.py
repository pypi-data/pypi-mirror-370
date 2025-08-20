"""Tests for the step() context manager functionality."""

import time

import pytest

from sdk_pytest_checkmate import step
from sdk_pytest_checkmate.plugin import StepRecord, _get_ctx


class TestStepContextManager:
    """Test the step() context manager functionality."""

    def test_step_basic_usage(self):
        """Test basic step context manager usage."""
        with step("Test step"):
            time.sleep(0.01)  # Small delay to test timing

        ctx = _get_ctx()
        steps = ctx["steps"]

        assert len(steps) == 1
        step_record = steps[0]
        assert isinstance(step_record, StepRecord)
        assert step_record.name == "Test step"
        assert step_record.seq == 0
        assert step_record.start > 0
        assert step_record.end is not None
        assert step_record.end > step_record.start
        assert step_record.error is None

    def test_step_with_exception(self):
        """Test step context manager when exception occurs."""
        with pytest.raises(ValueError):
            with step("Failing step"):
                raise ValueError("Test error")

        ctx = _get_ctx()
        steps = ctx["steps"]

        assert len(steps) == 1
        step_record = steps[0]
        assert step_record.name == "Failing step"
        assert step_record.error is not None
        assert "ValueError" in step_record.error
        assert "Test error" in step_record.error

    def test_multiple_steps_sequence(self):
        """Test multiple steps maintain correct sequence."""
        with step("First step"):
            pass

        with step("Second step"):
            pass

        with step("Third step"):
            pass

        ctx = _get_ctx()
        steps = ctx["steps"]

        assert len(steps) == 3
        assert steps[0].name == "First step"
        assert steps[0].seq == 0
        assert steps[1].name == "Second step"
        assert steps[1].seq == 1
        assert steps[2].name == "Third step"
        assert steps[2].seq == 2

    def test_nested_steps(self):
        """Test nested step context managers."""
        with step("Outer step"):
            with step("Inner step"):
                pass

        ctx = _get_ctx()
        steps = ctx["steps"]

        assert len(steps) == 2
        assert steps[0].name == "Outer step"
        assert steps[1].name == "Inner step"

    def test_step_to_dict_serialization(self):
        """Test step record serialization to dictionary."""
        with step("Serialization test"):
            pass

        ctx = _get_ctx()
        step_record = ctx["steps"][0]
        step_dict = step_record.to_dict()

        assert isinstance(step_dict, dict)
        assert step_dict["name"] == "Serialization test"
        assert step_dict["seq"] == 0
        assert "start" in step_dict
        assert "end" in step_dict
        assert step_dict["start"] <= step_dict["end"]
        assert "error" not in step_dict  # No error occurred

    def test_step_to_dict_with_error(self):
        """Test step record serialization when error occurred."""
        with pytest.raises(Exception):
            with step("Error test"):
                raise Exception("Test exception")

        ctx = _get_ctx()
        step_record = ctx["steps"][0]
        step_dict = step_record.to_dict()

        assert "error" in step_dict
        assert "Exception" in step_dict["error"]
        assert "Test exception" in step_dict["error"]
