from datetime import date, time, timedelta
from zoneinfo import ZoneInfo


class NyseCalendar:
    market_timezone = ZoneInfo("America/New_York")
    # The free SIP entitlement excludes the most recent 15 minutes. Waiting
    # until 16:15 ET also avoids treating an unfinished daily bar as final.
    completed_session_cutoff = time(16, 15)

    @staticmethod
    def _observed(day: date) -> date:
        if day.weekday() == 5:
            return day - timedelta(days=1)
        if day.weekday() == 6:
            return day + timedelta(days=1)
        return day

    @staticmethod
    def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
        day = date(year, month, 1)
        return day + timedelta(days=(weekday - day.weekday()) % 7 + 7 * (n - 1))

    @staticmethod
    def _last_weekday(year: int, month: int, weekday: int) -> date:
        day = date(year + (month == 12), month % 12 + 1, 1) - timedelta(days=1)
        return day - timedelta(days=(day.weekday() - weekday) % 7)

    def holidays(self, year: int) -> set[date]:
        return {
            self._observed(date(year, 1, 1)),
            self._nth_weekday(year, 1, 0, 3),
            self._nth_weekday(year, 2, 0, 3),
            self._last_weekday(year, 5, 0),
            self._observed(date(year, 6, 19)),
            self._observed(date(year, 7, 4)),
            self._nth_weekday(year, 9, 0, 1),
            self._nth_weekday(year, 11, 3, 4),
            self._observed(date(year, 12, 25)),
        }

    def is_trading_day(self, day: date) -> bool:
        return day.weekday() < 5 and day not in self.holidays(day.year)

    def previous_trading_day(self, day: date) -> date:
        candidate = day - timedelta(days=1)
        while not self.is_trading_day(candidate):
            candidate -= timedelta(days=1)
        return candidate

    def latest_completed_session(self, now=None) -> date:
        from django.utils import timezone

        current_time = now or timezone.now()
        if timezone.is_naive(current_time):
            current_time = timezone.make_aware(current_time, self.market_timezone)
        market_time = current_time.astimezone(self.market_timezone)
        current = market_time.date()
        if self.is_trading_day(current) and market_time.time() >= self.completed_session_cutoff:
            return current
        return self.previous_trading_day(current)

    def trading_days_between(self, start: date, end: date) -> list[date]:
        days = []
        current = start
        while current <= end:
            if self.is_trading_day(current):
                days.append(current)
            current += timedelta(days=1)
        return days
