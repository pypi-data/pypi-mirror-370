"""Pytest plugin for enriched HTML test reporting.

This plugin extends pytest with enhanced reporting capabilities including:

- **Test Steps**: Record named steps with timing using context managers
- **Soft Assertions**: Non-fatal assertions that collect failures without stopping tests
- **Data Attachments**: Attach arbitrary data objects to test timelines
- **Epic/Story Grouping**: Organize tests with @pytest.mark.epic and @pytest.mark.story
- **Interactive HTML Reports**: Rich reports with filtering, collapsible sections, and inline data

Quick Start:
    Install the plugin and use the three main functions in your tests:

    ```python
    from sdk_pytest_checkmate import step, soft_assert, add_data_report

    def test_user_workflow():
        with step("Setup user data"):
            user = create_test_user()
            add_data_report(user.__dict__, "Test User")

        with step("Login process"):
            login_response = login(user.username, user.password)
            soft_assert(login_response.ok, "Login should succeed")

        with step("Verify dashboard"):
            dashboard = get_dashboard()
            soft_assert("Welcome" in dashboard.title, "Dashboard should show welcome")
            add_data_report(dashboard.stats, "Dashboard Stats")
    ```

    Generate reports:
    ```bash
    pytest --report-html=report.html --report-title="My Test Suite"
    ```

Functions:
    step(name): Context manager for recording test steps with timing
    soft_assert(condition, message=None): Non-fatal assertion that continues test execution
    add_data_report(data, label): Attach arbitrary data to the test timeline

Markers:
    @pytest.mark.title(name): Set human-friendly test title
    @pytest.mark.epic(name): Group tests under an epic
    @pytest.mark.story(name): Group tests under a story (within an epic)
"""

from .plugin import add_data_report, soft_assert, step

__all__ = [
    "add_data_report",
    "soft_assert",
    "step",
]
