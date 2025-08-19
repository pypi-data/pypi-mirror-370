"""pytest-checkmate plugin.

A pytest plugin for enriched HTML test reporting with support for:
- Test steps with timing information
- Soft assertions that don't immediately fail tests
- Arbitrary data attachments to test timelines
- Epic and story grouping with markers
- Rich HTML reports with interactive filtering

The plugin automatically activates when installed and provides three main functions:
- step(): Context manager for recording test steps
- soft_assert(): Non-fatal assertions collected for later evaluation
- add_data_report(): Attach arbitrary data to test timeline

Example:
    Basic usage in a test:

    ```python
    def test_login_flow():
        with step("Navigate to login page"):
            driver.get("/login")

        with step("Enter credentials"):
            driver.find_element("username").send_keys("user")
            driver.find_element("password").send_keys("pass")

        soft_assert(login_button.is_enabled(), "Login button should be enabled")

        with step("Submit login"):
            login_button.click()

        add_data_report({"user": "testuser", "timestamp": time.time()}, "Login Data")

        assert "Dashboard" in driver.title
    ```

    Generate HTML report:
    ```bash
    pytest --report-html=report.html --report-title="My Test Report"
    ```
"""

from __future__ import annotations

import datetime as _dt
import html
import json as _json
import pathlib as _pl
import re
import time
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import pytest
from pytest import StashKey

__all__ = ["step", "soft_assert", "add_data_report"]


@dataclass
class StepRecord:
    """Record of a test step with timing and error information.

    This class represents a single step in a test execution timeline.
    Steps are created automatically when using the step() context manager.

    Attributes:
        name: Human-readable name of the step
        seq: Sequence number for ordering in timeline
        start: Unix timestamp when step started
        end: Unix timestamp when step finished (None if not finished)
        error: String representation of any error that occurred (None if no error)

    Example:
        ```python
        # Created automatically by step() context manager
        with step("Login user"):
            # Step record is created and tracked automatically
            perform_login()
        ```
    """

    name: str
    seq: int
    start: float
    end: float | None = None
    error: str | None = None

    def finish(self, error: BaseException | None) -> None:
        """Mark the step as finished and record any error.

        Args:
            error: Exception that occurred during step execution, or None if successful
        """
        self.end = time.time()
        if error is not None:
            self.error = repr(error)

    def to_dict(self) -> dict[str, object]:
        """Convert step record to dictionary for serialization.

        Returns:
            Dictionary containing all step information suitable for JSON serialization
        """
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end if self.end is not None else self.start,
            "seq": self.seq,
            **({"error": self.error} if self.error else {}),
        }


@dataclass
class SoftCheckRecord:
    """Record of a soft assertion with result and timing information.

    Soft assertions allow tests to continue execution even when conditions fail,
    collecting all failures for evaluation at the end of the test.

    Attributes:
        message: Descriptive message for the assertion
        passed: Whether the assertion condition was true
        seq: Sequence number for ordering in timeline
        time: Unix timestamp when assertion was made

    Example:
        ```python
        # Created automatically by soft_assert()
        soft_assert(element.is_displayed(), "Element should be visible")
        soft_assert(response.status_code == 200, "API should return 200")
        ```
    """

    message: str
    passed: bool
    seq: int
    time: float

    def to_dict(self) -> dict[str, object]:
        """Convert soft check record to dictionary for serialization.

        Returns:
            Dictionary containing all soft check information
        """
        return asdict(self)


@dataclass
class DataRecord:
    """Arbitrary user-provided data attached to a test timeline.

    Data records allow attaching any Python object to the test execution timeline.
    The data is serialized in the HTML report and can be expanded inline for inspection.

    Attributes:
        label: Short descriptive label shown in the report UI
        seq: Sequence number for ordering in timeline
        time: Unix timestamp when data was attached
        payload: The actual data object (dict/list will be pretty-printed as JSON)

    Example:
        ```python
        # API response data
        add_data_report({"status": 200, "data": response.json()}, "API Response")

        # Test configuration
        add_data_report(test_config, "Test Config")

        # Custom object
        add_data_report(user_profile.__dict__, "User Profile")
        ```
    """

    label: str
    seq: int
    time: float
    payload: Any

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "seq": self.seq,
            "time": self.time,
            "payload": self.payload,
        }


_ACTIVE_CONTEXT: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "_ACTIVE_CONTEXT", default=None
)
STASH_CTX: StashKey[Dict[str, Any]] = StashKey()
STASH_RESULTS: StashKey[list[dict[str, Any]]] = StashKey()


@pytest.fixture(autouse=True)
def _checkmate_context():
    ctx: Dict[str, Any] = {
        "steps": [],
        "soft_failures": [],
        "soft_checks": [],
        "data_reports": [],
        "seq": 0,
    }
    token = _ACTIVE_CONTEXT.set(ctx)
    try:
        yield ctx
    finally:
        _ACTIVE_CONTEXT.reset(token)


def _get_ctx() -> Dict[str, Any]:
    ctx = _ACTIVE_CONTEXT.get()
    if ctx is None:
        raise RuntimeError("Used outside of a test")
    return ctx


class _StepCtx:
    def __init__(self, name: str):
        self.name = name
        self._record: StepRecord | None = None
        ctx = _get_ctx()
        seq = ctx.get("seq", 0)
        ctx["seq"] = seq + 1
        rec = StepRecord(name=self.name, seq=seq, start=time.time(), end=None)
        ctx["steps"].append(rec)
        self._record = rec

    def __enter__(self):
        if self._record is not None:
            self._record.start = time.time()
            self._record.end = None
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._record is not None:
            self._record.finish(exc)
        return False

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc, tb):
        return self.__exit__(exc_type, exc, tb)


def step(name: str) -> _StepCtx:
    """Create and register a step in the current test timeline.

    The returned object is a context manager supporting both ``with`` and
    ``async with`` usage. Entering the context records the start timestamp;
    exiting records the end timestamp and captures any raised exception.

    Parameters
    ----------
    name: str
        Human‑readable step name that will appear in the HTML report.

    Returns
    -------
    _StepCtx
        Context manager representing the step.

    Examples
    --------
    with step("Login"):
        do_login()

    async with step("Async fetch"):
        await fetch()
    """
    return _StepCtx(name)


def soft_assert(condition: bool, message: str | None = None) -> bool:
    """Record a non-fatal ("soft") assertion that doesn't immediately fail the test.

    Unlike regular ``assert`` statements, a failing soft assertion allows the test
    to continue execution. All soft assertion failures are collected and the test
    is marked as failed at the end if any soft assertions failed.

    This is useful for validating multiple conditions in a single test without
    stopping at the first failure, providing a complete picture of what passed
    and what failed.

    Args:
        condition: The boolean expression to evaluate. True means assertion passed.
        message: Optional descriptive message explaining what is being asserted.
                If not provided, defaults to "Soft assertion".

    Returns:
        The boolean value of ``condition``, allowing for fluent usage patterns.

    Raises:
        RuntimeError: If called outside of a test context.

    Example:
        ```python
        def test_user_profile():
            user = get_user_profile()

            # Multiple soft assertions - test continues even if some fail
            soft_assert(user.name is not None, "User should have a name")
            soft_assert(user.email.endswith("@company.com"), "Email should be company domain")
            soft_assert(len(user.permissions) > 0, "User should have permissions")
            soft_assert(user.is_active, "User should be active")

            # Test continues and all failures are reported together
            # Final assertion can still be used for critical failures
            assert user.id is not None, "User ID is required"
        ```

    Note:
        The test will be marked as failed at the end of execution if any soft
        assertions failed, with a summary of all failures displayed.
    """
    ctx = _get_ctx()
    msg = message or "Soft assertion"
    seq = ctx.get("seq", 0)
    ctx["seq"] = seq + 1
    rec = SoftCheckRecord(
        message=msg, passed=bool(condition), time=time.time(), seq=seq
    )
    ctx["soft_checks"].append(rec)
    if not condition:
        ctx["soft_failures"].append(msg)
    return bool(condition)


def add_data_report(data: Any, label: str) -> DataRecord:
    """Attach arbitrary data to the test timeline for inspection in HTML reports.

    This function allows you to attach any Python object to the test execution
    timeline. The data is captured with a timestamp and sequence number, then
    serialized in the HTML report where it can be expanded inline for inspection.

    The data appears in the timeline alongside steps and soft assertions, maintaining
    the chronological order of test execution events.

    Args:
        data: Any Python object to attach. Dictionaries and lists are pretty-printed
              as JSON in the report. Other objects are converted to string representation.
        label: Short descriptive label shown as the clickable summary in the report UI.
               This should be concise but descriptive (e.g., "API Response", "Test Config").

    Returns:
        DataRecord: The internal record object containing the data, timestamp, and metadata.
                   Usually not needed but available for advanced use cases.

    Raises:
        RuntimeError: If called outside of a test context.

    Example:
        ```python
        def test_api_integration():
            # Attach configuration data
            config = {"endpoint": "/api/users", "timeout": 30}
            add_data_report(config, "API Config")

            response = api_client.get("/api/users")

            # Attach response data for debugging
            add_data_report({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json()
            }, "API Response")

            # Attach custom objects
            user_data = process_response(response)
            add_data_report(user_data.__dict__, "Processed User Data")

            assert response.status_code == 200
        ```

    Note:
        - Data is serialized at report generation time, not when this function is called
        - Large objects should be avoided as they can make reports unwieldy
        - Sensitive data (passwords, tokens) should not be included in reports
    """
    ctx = _get_ctx()
    seq = ctx.get("seq", 0)
    ctx["seq"] = seq + 1
    record = DataRecord(label=label, seq=seq, time=time.time(), payload=data)
    ctx["data_reports"].append(record)
    return record


def pytest_addoption(parser):
    g = parser.getgroup("checkmate")
    g.addoption(
        "--report-html",
        action="store",
        nargs="?",
        const="report.html",
        dest="report_html",
        help="Generate HTML report (optional path, default: report.html)",
    )
    g.addoption(
        "--report-title",
        action="store",
        dest="report_title",
        default="Pytest report",
        help="Title for the HTML report header and <title>.",
    )
    g.addoption(
        "--report-json",
        action="store",
        dest="report_json",
        default=None,
        help="Path to write JSON results (optional).",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "title(name): Human friendly test title")
    config.addinivalue_line("markers", "epic(name): Epic grouping marker")
    config.addinivalue_line(
        "markers", "story(name): Story grouping marker (nested under epic)"
    )
    config.stash[STASH_RESULTS] = []
    config._checkmate_start_time = time.time()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "setup":
        try:
            item.stash[STASH_CTX] = _get_ctx()
        except RuntimeError:
            pass

    if rep.when == "call":
        ctx = item.stash.get(STASH_CTX, None)
        if ctx and ctx["soft_failures"] and rep.passed:
            lines = [f"Soft assertion failures ({len(ctx['soft_failures'])}):"] + [
                f" {i + 1}. {m}" for i, m in enumerate(ctx["soft_failures"])
            ]
            rep.outcome = "failed"
            rep.longrepr = "\n".join(lines)

    record_now = False
    if rep.when == "call":
        record_now = True
    elif rep.when == "setup" and (rep.skipped or rep.failed):
        record_now = True
    elif rep.when == "teardown" and rep.failed:
        record_now = True

    if not record_now:
        return

    status: Optional[str] = None
    if rep.skipped:
        status = "XFAIL" if getattr(rep, "wasxfail", False) else "SKIPPED"
    elif rep.failed:
        status = (
            "XFAIL"
            if getattr(rep, "wasxfail", False)
            else ("FAILED" if rep.when == "call" else "ERROR")
        )
    elif rep.passed:
        status = "XPASS" if getattr(rep, "wasxfail", False) else "PASSED"

    title_marker = item.get_closest_marker("title")
    title = title_marker.args[0] if title_marker and title_marker.args else item.name
    ctx = item.stash.get(STASH_CTX, None)
    steps: list[StepRecord] = ctx["steps"] if ctx else []
    soft_checks: list[SoftCheckRecord] = ctx["soft_checks"] if ctx else []
    data_reports: list[DataRecord] = ctx["data_reports"] if ctx else []

    full_details = ""
    short_details = ""
    if (status in {"XFAIL", "XPASS"}) and getattr(rep, "wasxfail", None):
        reason = str(getattr(rep, "wasxfail", ""))
        short_details = full_details = reason
    elif rep.failed or rep.outcome == "failed":
        full_details = str(rep.longrepr) if rep.longrepr else ""
        if full_details.startswith("Soft assertion failures"):
            short_details = full_details
        else:
            lines = full_details.splitlines()
            short_details = next(
                (ln[2:].strip() for ln in lines if ln.startswith("E ")), ""
            )
            if not short_details and lines:
                short_details = lines[-1].strip()
    elif rep.skipped:
        if isinstance(rep.longrepr, tuple):
            full_details = rep.longrepr[2]  # type: ignore[index]
        else:
            full_details = str(rep.longrepr) if rep.longrepr else ""
        short_details = full_details

    epic_marker = item.get_closest_marker("epic")
    story_marker = item.get_closest_marker("story")
    epic = epic_marker.args[0] if epic_marker and epic_marker.args else None
    story = story_marker.args[0] if story_marker and story_marker.args else None

    item.config.stash[STASH_RESULTS].append(
        {
            "name": item.name,
            "title": title,
            "status": status or rep.outcome.upper(),
            "duration": rep.duration,
            "short": short_details,
            "full": full_details,
            "steps": [s.to_dict() if isinstance(s, StepRecord) else s for s in steps],
            "soft_checks": [
                sc.to_dict() if isinstance(sc, SoftCheckRecord) else sc
                for sc in soft_checks
            ],
            "data_reports": [
                dr.to_dict() if isinstance(dr, DataRecord) else dr
                for dr in data_reports
            ],
            "epic": epic,
            "story": story,
        }
    )


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    report_opt = config.getoption("report_html")
    if not report_opt:
        return
    results: List[Dict[str, Any]] = config.stash.get(STASH_RESULTS, [])
    if not results:
        return
    start_ts = getattr(config, "_checkmate_start_time", None)
    end_ts = time.time()
    if start_ts is not None:
        duration_total = end_ts - float(start_ts)
        start_str = _dt.datetime.fromtimestamp(float(start_ts)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        end_str = _dt.datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S")
        duration_str = f"{duration_total:.3f}s"
    else:
        start_str = end_str = duration_str = "—"

    def esc(s: str) -> str:
        return html.escape(s, quote=True)

    json_path_opt = config.getoption("report_json")
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")

    if json_path_opt:
        try:
            p = _pl.Path(json_path_opt)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                _json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as exc:
            if terminal:
                terminal.write_line(
                    f"checkmate: failed to write JSON report '{json_path_opt}': {exc}"
                )

    title_opt = config.getoption("report_title") or "Pytest report"
    esc_title = esc(title_opt)

    css = """
    body { font-family: -apple-system, Arial, sans-serif; margin:0; padding:0 0 60px 0; background:#f6f8fa; }
    header { background:#e8f1ff; padding:14px 24px; font-size:20px; font-weight:600; text-align:center; }
    .summary { display:flex; gap:12px; flex-wrap:wrap; padding:12px 24px; justify-content:center; }
    .badge { border:1px solid #3332; border-radius:999px; padding:6px 14px; cursor:pointer; font-size:13px; background:#fff; }
    .badge[data-status="PASSED"] { background:#d4f7d9; }
    .badge[data-status="FAILED"] { background:#ffd8d6; }
    .badge[data-status="ERROR"] { background:#ffe1b3; }
    .badge[data-status="SKIPPED"] { background:#fff5cc; }
    .badge[data-status="XFAIL"], .badge[data-status="XPASS"] { background:#e6dcff; }
    table { border-collapse:collapse; width:100%; background:#fff; }
    th, td { border:1px solid #d0d7de; padding:6px 8px; font-size:13px; vertical-align:top; }
    th { background:#f0f6ff; text-align:left; }
    .details { white-space:pre-wrap; font-family:Menlo, monospace; max-width:480px; max-height:240px; overflow:auto; }
    tr.status-PASSED td.details { color:#1a7f37; }
    tr.status-FAILED td.details { color:#b30000; }
    tr.status-ERROR td.details { color:#c85500; }
    tr.status-SKIPPED td.details { color:#8a6d00; }
    tr.status-XFAIL td.details, tr.status-XPASS td.details { color:#6941c6; }
    .steps { margin:4px 0 0 0; padding:0 0 0 28px; list-style:decimal; }
    .checks { list-style:none; margin:4px 0 4px 0; padding-left:28px; }
    .checks li { font-size:12px; }
    .data-items { list-style:none; margin:2px 0 2px 0; padding-left:24px; }
    .data-items .data-item { list-style:none; }
    .checks li.fail { color:#c40000; font-weight:600; }
    .checks li.pass { color:#1a7f37; }
    .step-error { color:#c40000; font-weight:600; }
    .data-item { margin:4px 0; }
    .data-item .data-summary { cursor:pointer; font-weight:500; color:#0366d6; }
    .data-item .data-summary::before { content:'▶'; display:inline-block; margin-right:4px; transition:transform .18s ease; }
    .data-item.expanded .data-summary::before { transform:rotate(90deg); }
    .data-item .data-details { margin:4px 0 0 18px; }
    .data-item .data-details pre { 
        max-width:100%;
        box-sizing:border-box;
        padding:8px 10px;
        margin:4px 0;
        border:1px solid #d0d7de;
        background:#f6f8fa;
        border-radius:4px;
        font-size:12px;
        line-height:1.4;
        white-space:pre-wrap;
        word-break:break-word;
        overflow-x:auto;
        overflow-y:auto;
        max-height:340px;
    }
    .data-item .data-details pre { overflow-wrap:anywhere; }
    .errors-block { border:1px solid #e99; background:#ffecec; padding:8px 12px; margin-top:12px; border-radius:4px; }
    .errors-block h4 { margin:0 0 6px 0; color:#b30000; }
    footer { position:fixed; bottom:0; left:0; right:0; background:#e8f1ff; padding:8px 16px; font-size:12px; color:#555; text-align:center; border-top:1px solid #d0d7de; }
    .hidden { display:none; }
    tr.main-row { cursor:pointer; }
    tr.detail-row td { background:#f3f6f9; }
    .detail-card { background:#fff; border:1px solid #d0d7de; border-left:6px solid #888; padding:10px 16px 14px 16px; border-radius:6px; max-width:880px; margin:6px auto; box-shadow:0 2px 4px -2px rgba(0,0,0,0.12); }
    .detail-card.status-PASSED { border-left-color:#1a7f37; }
    .detail-card.status-FAILED { border-left-color:#b30000; }
    .detail-card.status-ERROR { border-left-color:#c85500; }
    .detail-card.status-SKIPPED { border-left-color:#8a6d00; }
    .detail-card.status-XFAIL { border-left-color:#6941c6; }
    .detail-card.status-XPASS { border-left-color:#6941c6; }
    .detail-card h4 { margin-top:14px; }
    .run-info { max-width:960px; margin:8px auto 4px; padding:6px 16px 10px; font-size:12px; color:#444; display:flex; flex-wrap:wrap; gap:18px; justify-content:center; }
    .run-info div { white-space:nowrap; }
    td.status-cell { font-weight:600; }
    td.status-cell .st-PASSED { color:#1a7f37; }
    td.status-cell .st-FAILED { color:#b30000; }
    td.status-cell .st-ERROR { color:#c85500; }
    td.status-cell .st-SKIPPED { color:#8a6d00; }
    td.status-cell .st-XFAIL { color:#6941c6; }
    td.status-cell .st-XPASS { color:#6941c6; }
    
    .collapsible > .toggle { cursor:pointer; position:relative; user-select:none; }
    .collapsible > .toggle::before { content:'▶'; display:inline-block; margin-right:6px; transition:transform .18s ease; color:#555; }
    .collapsible.expanded > .toggle::before { transform:rotate(90deg); }
    .group-body, .story-body { padding:0 4px 4px; }
    .story-block { margin:10px auto 18px; max-width:1280px; background:#0000; }
    .story-block > .toggle { font-weight:600; }
    .story-block table { margin-top:2px; }
    .group-section { max-width:1280px; margin:0 auto; }
    /* Epic & Story heading sizing/alignment */
    .group-section h2.toggle { font-size:20px !important; text-align:left !important; padding:0 24px; }
    .story-block h3.toggle { font-size:18px !important; text-align:left !important; padding:0 28px; }
    """

    def format_timeline(
        steps: List[Dict[str, Any]],
        soft: List[Dict[str, Any]],
        data_reports: List[Dict[str, Any]],
    ) -> str:
        seq: List[tuple[int, str, Dict[str, Any]]] = []
        for s in steps:
            seq.append((s.get("seq", 0), "step", s))
        for sc in soft:
            seq.append((sc.get("seq", 0), "soft", sc))
        for dr in data_reports:
            seq.append((dr.get("seq", 0), "data", dr))
        if not seq:
            return ""
        seq.sort(key=lambda x: x[0])

        def fmt_duration(sd: Dict[str, Any]) -> str:
            if "start" in sd and "end" in sd:
                try:
                    d = sd["end"] - sd["start"]
                    if d >= 0.001:
                        return f" ({d:.3f}s)"
                except Exception:
                    return ""
            return ""

        def render_data(dr: Dict[str, Any]) -> str:
            summary = esc(dr.get("label", "data"))
            payload = dr.get("payload")
            try:
                if isinstance(payload, (dict, list)):
                    pretty = _json.dumps(payload, ensure_ascii=False, indent=2)
                    details = f"<pre>{esc(pretty)}</pre>"
                else:
                    details = f"<pre>{esc(str(payload))}</pre>"
            except Exception:
                details = f"<pre>{esc(str(payload))}</pre>"
            return (
                "<li class='data-item'>DATA: "
                f"<span class='data-summary'>{summary}</span>"
                f"<div class='data-details hidden'>{details}</div></li>"
            )

        def render_check(chk: Dict[str, Any]) -> str:
            cls = "pass" if chk.get("passed") else "fail"
            icon = "✔" if chk.get("passed") else "✖"
            return (
                "<ul class='checks'><li class='"
                + cls
                + "'>CHECK: "
                + icon
                + " "
                + esc(chk.get("message", ""))
                + "</li></ul>"
            )

        pre_checks: List[str] = []
        pre_data_html: List[str] = []
        pos = 0
        while pos < len(seq) and seq[pos][1] != "step":
            kind = seq[pos][1]
            obj = seq[pos][2]
            if kind == "soft":
                pre_checks.append(render_check(obj))
            else:
                pre_data_html.append(
                    "<ul class='data-items'>" + render_data(obj) + "</ul>"
                )
            pos += 1

        out: List[str] = ["<h4>Full details</h4>"]
        if pre_checks or pre_data_html:
            out.append(
                "<div class='pre-checks'>"
                + "".join(pre_checks + pre_data_html)
                + "</div>"
            )

        steps_markup: List[str] = []
        current_step: Dict[str, Any] | None = None
        attachments: List[str] = []
        for _, kind, obj in seq[pos:]:
            if kind == "step":
                if current_step is not None:
                    steps_markup.append(
                        "<li>STEP: "
                        + esc(current_step.get("name", ""))
                        + fmt_duration(current_step)
                        + ""
                        + "".join(attachments)
                        + "</li>"
                    )
                current_step = obj
                attachments = []
            elif kind == "soft":
                attachments.append(render_check(obj))
            else:
                attachments.append(
                    "<ul class='data-items'>" + render_data(obj) + "</ul>"
                )
        if current_step is not None:
            steps_markup.append(
                "<li>STEP: "
                + esc(current_step.get("name", ""))
                + fmt_duration(current_step)
                + ""
                + "".join(attachments)
                + "</li>"
            )

        out.append("<ol class='steps'>" + "".join(steps_markup) + "</ol>")
        return "".join(out)

    def format_errors(r: Dict[str, Any]) -> str:
        status = r.get("status")
        steps = r.get("steps", [])
        soft = r.get("soft_checks", [])
        failed_soft = [s for s in soft if not s.get("passed")]
        step_errors = [s for s in steps if s.get("error")]
        failure_text = r.get("full", "") if status in {"FAILED", "ERROR"} else ""
        parts: List[str] = []
        if failure_text:
            parts.append(f"<pre class='details'>{esc(failure_text)}</pre>")
        if status in {"SKIPPED", "XFAIL", "XPASS"}:
            reason = r.get("full", "")
            if reason:
                parts.append(f"<pre class='details'>{esc(reason)}</pre>")
        if step_errors:
            li = [
                f"<li><span class='step-error'>Step '{esc(s.get('name', ''))}': {esc(str(s.get('error')))}</span></li>"
                for s in step_errors
            ]
            parts.append(
                "<ul style='margin:4px 0 8px 16px;padding:0;'>" + "".join(li) + "</ul>"
            )
        if failed_soft and not failure_text.startswith("Soft assertion failures"):
            li = [
                f"<li style='color:#c40000;font-weight:600;'>✖ {esc(s['message'])}</li>"
                for s in failed_soft
            ]
            parts.append(
                "<ul style='margin:4px 0 8px 16px;padding:0;'>" + "".join(li) + "</ul>"
            )
        if not parts:
            return ""
        return "<div class='errors-block'><h4>Errors</h4>" + "".join(parts) + "</div>"

    grouped: Dict[str, Dict[Optional[str], List[Dict[str, Any]]]] = {}
    ungrouped: List[Dict[str, Any]] = []
    for r in results:
        epic = r.get("epic")
        story = r.get("story")
        if epic is None and story is None:
            ungrouped.append(r)
            continue
        epic_key = epic or "<no-epic>"
        grouped.setdefault(epic_key, {})
        grouped[epic_key].setdefault(story, []).append(r)

    def compute_counts(sub: List[Dict[str, Any]]) -> Dict[str, int]:
        c: Dict[str, int] = {}
        for r in sub:
            c[r["status"]] = c.get(r["status"], 0) + 1
        return c

    row_index = 0

    def build_rows(sub_results: List[Dict[str, Any]], group_id: str) -> str:
        nonlocal row_index
        rows: List[str] = []
        for r in sub_results:
            idx = row_index
            row_index += 1
            short = esc(r.get("short", ""))
            timeline_html = format_timeline(
                r.get("steps", []), r.get("soft_checks", []), r.get("data_reports", [])
            )
            errors_html = format_errors(r)
            expanded = f"<div class='detail-card status-{r['status']}'>{timeline_html}{errors_html}</div>"
            rows.append(
                f"<tr class='status-{r['status']} main-row' data-group='{group_id}' data-status='{r['status']}' data-idx='{idx}'><td>{esc(r['title'])}</td>"
                f"<td class='status-cell'><span class='st-{r['status']}'>{r['status']}</span></td><td>{r['duration']:.3f}</td><td class='details'>{short}</td></tr>"
                f"<tr class='status-{r['status']} detail-row hidden manual-hidden' data-group='{group_id}' data-status='{r['status']}' data-idx='{idx}'><td colspan='4'>{expanded}</td></tr>"
            )
        return "".join(rows)

    def build_badges(sub_results: List[Dict[str, Any]], group_id: str) -> str:
        counts = compute_counts(sub_results)
        total_local = sum(counts.values())
        desired = ["PASSED", "FAILED", "SKIPPED", "XFAIL"]
        ordered = [k for k in desired if k in counts] + [
            k for k in counts.keys() if k not in desired
        ]
        parts = [
            f"<div class='badge' data-group='{group_id}' data-status='ALL'>ALL {total_local}</div>"
        ]
        parts += [
            f"<div class='badge' data-group='{group_id}' data-status='{esc(k)}'>{k} {counts[k]}</div>"
            for k in ordered
        ]
        return "".join(parts)

    sections: List[str] = []
    if ungrouped:
        gid = "ungrouped"
        sections.append(
            f"<section class='group-section'>"
            f"<div class='summary' data-group='{gid}'>{build_badges(ungrouped, gid)}</div>"
            f"<table><thead><tr><th>Test</th><th>Status</th><th>Duration (s)</th><th>Details</th></tr></thead><tbody>{build_rows(ungrouped, gid)}</tbody></table></section>"
        )

    def slugify(raw: str) -> str:
        raw = raw.strip().lower().replace(" ", "-")
        return re.sub(r"[^a-z0-9_-]", "_", raw) or "group"

    for epic_key in sorted(grouped.keys()):
        stories = grouped[epic_key]
        epic_display = esc(epic_key if epic_key != "<no-epic>" else "(No epic)")
        epic_all: List[Dict[str, Any]] = []
        for lst in stories.values():
            epic_all.extend(lst)
        has_story = any(k is not None for k in stories.keys())
        if has_story:
            story_blocks: List[str] = []
            for story_key in sorted(
                stories.keys(), key=lambda x: ("" if x is None else str(x).lower())
            ):
                story_list = stories[story_key]
                story_display = (
                    esc(story_key) if story_key is not None else "(No story)"
                )
                gid = f"epic-{slugify(epic_key)}-story-{slugify(str(story_key))}"
                story_blocks.append(
                    f"<div class='story-block collapsible' data-kind='story'>"
                    f"<h3 class='toggle' style='margin:14px 0 4px;'>Story: {story_display}</h3>"
                    f"<div class='story-body hidden'><div class='summary' data-group='{gid}'>{build_badges(story_list, gid)}</div>"
                    f"<table><thead><tr><th>Test</th><th>Status</th><th>Duration (s)</th><th>Details</th></tr></thead><tbody>{build_rows(story_list, gid)}</tbody></table></div>"
                    f"</div>"
                )
            sections.append(
                f"<section class='group-section collapsible' data-kind='epic'>"
                f"<h2 class='toggle' style='margin:36px 0 4px;'>Epic: {epic_display}</h2>"
                f"<div class='group-body hidden'>{''.join(story_blocks)}</div>"
                f"</section>"
            )
        else:
            gid = f"epic-{slugify(epic_key)}"
            sections.append(
                f"<section class='group-section collapsible' data-kind='epic'>"
                f"<h2 class='toggle' style='margin:36px 0 4px;'>Epic: {epic_display}</h2>"
                f"<div class='group-body hidden'><div class='summary' data-group='{gid}'>{build_badges(epic_all, gid)}</div>"
                f"<table><thead><tr><th>Test</th><th>Status</th><th>Duration (s)</th><th>Details</th></tr></thead><tbody>{build_rows(epic_all, gid)}</tbody></table></div>"
                f"</section>"
            )

    script_js = r"""
function filterStatusGroup(groupId, status) {
    const selector = 'tr.main-row[data-group="'+groupId+'"]';
    document.querySelectorAll(selector).forEach(tr=>{
        const idx = tr.dataset.idx;
        const detail = document.querySelector('tr.detail-row[data-idx="'+idx+'"]');
        const match = !status || tr.dataset.status===status;
        if(match){ tr.classList.remove('hidden'); if(detail) detail.classList.add('hidden'); }
        else { tr.classList.add('hidden'); if(detail) detail.classList.add('hidden'); }
    });
}

document.addEventListener('DOMContentLoaded', ()=>{
    document.querySelectorAll('.summary').forEach(sumEl=>{
        const groupId = sumEl.getAttribute('data-group');
        if(!groupId) return;
        sumEl.querySelectorAll('.badge').forEach(b=>{
            b.addEventListener('click', ()=>{
                const st = b.dataset.status === 'ALL'? null : b.dataset.status;
                filterStatusGroup(groupId, st);
            });
        });
    });

    document.querySelectorAll('tr.main-row').forEach(row=>{
        row.addEventListener('click',()=>{
            const idx = row.dataset.idx;
            const detail = document.querySelector('tr.detail-row[data-idx="'+idx+'"]');
            if(detail){ detail.classList.toggle('hidden'); detail.classList.toggle('manual-hidden'); }
        });
    });

    // Data record expand/collapse
    document.body.addEventListener('click', (e)=>{
        const t = e.target;
        if(!(t instanceof HTMLElement)) return;
        if(t.classList.contains('data-summary')){
            const li = t.closest('.data-item');
            if(!li) return;
            const details = li.querySelector('.data-details');
            if(details){ details.classList.toggle('hidden'); li.classList.toggle('expanded'); }
        }
    });

    // Collapsible epics & stories
    document.querySelectorAll('.collapsible > .toggle').forEach(tg=>{
        tg.addEventListener('click', (e)=>{
            e.stopPropagation();
            const parent = tg.parentElement;
            if(!parent) return;
            parent.classList.toggle('expanded');
            const body = parent.querySelector('.group-body, .story-body');
            if(body) body.classList.toggle('hidden');
        });
    });
});
"""

    html_doc = """<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<title>{esc_title}</title>
<style>{css}</style>
</head>
<body>
<header>{esc_title}</header>
<div class='run-info'>
    <div>Start time: {start_time}</div>
    <div>End time: {end_time}</div>
    <div>Total duration: {total_time}</div>
</div>
{sections}
<footer>Generated by pytest-checkmate</footer>
<script>{js}</script>
</body>
</html>""".format(
        css=css,
        sections="".join(sections)
        or "<p style='padding:12px 24px;'>No tests collected.</p>",
        start_time=esc(start_str),
        end_time=esc(end_str),
        total_time=esc(duration_str),
        esc_title=esc_title,
        js=script_js,
    )

    report_path = (
        (session.config.rootpath / report_opt)
        if isinstance(report_opt, str)
        else (session.config.rootpath / "report.html")
    )
    report_path = _pl.Path(report_path)
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(html_doc, encoding="utf-8")
        if terminal:
            terminal.write_line(f"checkmate: wrote HTML report to {report_path}")
    except Exception as exc:
        if terminal:
            terminal.write_line(
                f"checkmate: failed to write HTML report '{report_path}': {exc}"
            )
