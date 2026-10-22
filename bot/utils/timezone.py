from datetime import datetime, timezone, timedelta

# Часовой пояс UTC+5
UTC_PLUS_5 = timezone(timedelta(hours=5))


def now() -> datetime:
    """Получить текущее время в часовом поясе UTC+5"""
    return datetime.now(UTC_PLUS_5)
