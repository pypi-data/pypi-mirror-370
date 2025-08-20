"""Integration tests combining step, soft_assert, and add_data_report."""

import time

import pytest

from sdk_pytest_checkmate import add_data_report, soft_assert, step
from sdk_pytest_checkmate.plugin import _get_ctx


class TestIntegration:
    """Test integration between different plugin features."""

    def test_combined_functionality(self):
        """Test step, soft_assert, and add_data_report working together."""
        with step("Setup phase"):
            config = {"timeout": 30, "retries": 3}
            add_data_report(config, "Test Config")
            soft_assert(config["timeout"] > 0, "Timeout should be positive")

        with step("Execution phase"):
            result = {"status": "success", "data": [1, 2, 3]}
            add_data_report(result, "Execution Result")
            soft_assert(result["status"] == "success", "Should succeed")
            soft_assert(len(result["data"]) == 3, "Should have 3 items")

        with step("Verification phase"):
            verification = {"checks_passed": 2, "checks_failed": 0}
            add_data_report(verification, "Verification Stats")
            soft_assert(verification["checks_failed"] == 0, "No failures expected")

        # Verify all data was recorded
        ctx = _get_ctx()
        assert len(ctx["steps"]) == 3
        assert len(ctx["soft_checks"]) == 4
        assert len(ctx["data_reports"]) == 3
        assert len(ctx["soft_failures"]) == 0

    def test_sequence_ordering(self):
        """Test that steps, soft_assert, and data_report maintain proper sequence."""
        # Mix different operations to test sequence numbering
        add_data_report("initial", "Initial Data")  # seq: 0

        with step("First step"):  # seq: 1
            soft_assert(True, "First assertion")  # seq: 2
            add_data_report("step1", "Step 1 Data")  # seq: 3

        soft_assert(True, "Outside assertion")  # seq: 4

        with step("Second step"):  # seq: 5
            add_data_report("step2", "Step 2 Data")  # seq: 6
            soft_assert(True, "Second assertion")  # seq: 7

        add_data_report("final", "Final Data")  # seq: 8

        ctx = _get_ctx()

        # Check sequences
        assert ctx["data_reports"][0].seq == 0  # Initial Data
        assert ctx["steps"][0].seq == 1  # First step
        assert ctx["soft_checks"][0].seq == 2  # First assertion
        assert ctx["data_reports"][1].seq == 3  # Step 1 Data
        assert ctx["soft_checks"][1].seq == 4  # Outside assertion
        assert ctx["steps"][1].seq == 5  # Second step
        assert ctx["data_reports"][2].seq == 6  # Step 2 Data
        assert ctx["soft_checks"][2].seq == 7  # Second assertion
        assert ctx["data_reports"][3].seq == 8  # Final Data

    def test_nested_steps_with_mixed_operations(self):
        """Test nested steps combined with other operations."""
        with step("Outer step"):
            add_data_report("outer_start", "Outer Start")
            soft_assert(True, "Outer assertion")

            with step("Inner step"):
                add_data_report("inner", "Inner Data")
                soft_assert(True, "Inner assertion")

            add_data_report("outer_end", "Outer End")
            soft_assert(True, "Final outer assertion")

        ctx = _get_ctx()
        assert len(ctx["steps"]) == 2
        assert len(ctx["soft_checks"]) == 3
        assert len(ctx["data_reports"]) == 3

    def test_error_in_step_with_other_operations(self):
        """Test behavior when step fails but other operations succeed."""
        add_data_report("before_error", "Before Error")

        with pytest.raises(ValueError):
            with step("Failing step"):
                soft_assert(True, "Before error")
                add_data_report("in_error_step", "In Error Step")
                raise ValueError("Test error")

        # Operations after error should still work
        soft_assert(True, "After error")
        add_data_report("after_error", "After Error")

        ctx = _get_ctx()

        # Step should have error recorded
        assert len(ctx["steps"]) == 1
        assert ctx["steps"][0].error is not None
        assert "ValueError" in ctx["steps"][0].error

        # Other operations should still be recorded
        assert len(ctx["soft_checks"]) == 2
        assert len(ctx["data_reports"]) == 3

    def test_soft_assert_failures_collection(self):
        """Test that soft assertion failures are properly collected."""
        with step("Testing multiple failures"):
            soft_assert(True, "This passes")
            soft_assert(False, "First failure")
            soft_assert(True, "This also passes")
            soft_assert(False, "Second failure")
            soft_assert(False, "Third failure")
            add_data_report({"failed_count": 3}, "Failure Stats")

        ctx = _get_ctx()

        assert len(ctx["soft_checks"]) == 5
        assert len(ctx["soft_failures"]) == 3

        expected_failures = ["First failure", "Second failure", "Third failure"]
        assert ctx["soft_failures"] == expected_failures

        # Check individual soft check records
        checks = ctx["soft_checks"]
        assert checks[0].passed is True  # "This passes"
        assert checks[1].passed is False  # "First failure"
        assert checks[2].passed is True  # "This also passes"
        assert checks[3].passed is False  # "Second failure"
        assert checks[4].passed is False  # "Third failure"

    def test_performance_with_many_operations(self):
        """Test performance with many operations."""
        start_time = time.time()

        # Perform many operations
        for i in range(50):
            with step(f"Step {i}"):
                soft_assert(i % 2 == 0 or i % 2 == 1, f"Math check {i}")
                if i % 10 == 0:
                    add_data_report({"iteration": i}, f"Checkpoint {i}")

        end_time = time.time()
        execution_time = end_time - start_time

        ctx = _get_ctx()

        # Verify all operations were recorded
        assert len(ctx["steps"]) == 50
        assert len(ctx["soft_checks"]) == 50
        assert len(ctx["data_reports"]) == 5  # Every 10th iteration

        # Performance should be reasonable (adjust threshold as needed)
        assert execution_time < 1.0, f"Execution took too long: {execution_time}s"
