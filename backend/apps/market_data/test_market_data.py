from datetime import UTC, datetime

from .calendar import NyseCalendar


def test_latest_completed_session_uses_new_york_market_close():
    calendar = NyseCalendar()

    assert calendar.latest_completed_session(datetime(2026, 9, 14, 12, tzinfo=UTC)).isoformat() == (
        "2026-09-11"
    )
    assert calendar.latest_completed_session(datetime(2026, 9, 14, 21, tzinfo=UTC)).isoformat() == (
        "2026-09-14"
    )


def test_latest_completed_session_rolls_weekends_back():
    calendar = NyseCalendar()

    assert calendar.latest_completed_session(datetime(2026, 9, 13, 18, tzinfo=UTC)).isoformat() == (
        "2026-09-11"
    )
