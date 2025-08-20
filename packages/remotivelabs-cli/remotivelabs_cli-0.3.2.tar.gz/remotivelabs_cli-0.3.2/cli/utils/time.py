from datetime import date, datetime


def parse_date(date_str: str) -> date:
    return parse_datetime(date_str).date()


def parse_datetime(date_str: str) -> datetime:
    """Required for pre 3.11"""
    normalized = date_str.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)
