from datetime import datetime, timezone
# GitHub states clearly in https://docs.github.com/en/rest/using-the-rest-api/timezones-and-the-rest-api?apiVersion=2022-11-28
# that "Timestamps returned by the API are in UTC time, ISO 8601 format."
# Therefore we need to handle as UTC every date we process.
def parse_date(date_str):
    # Parse the ISO 8601 date, keeping timezone information
    if date_str.endswith('Z'):
        date_str = date_str[:-1] + '+00:00'  # Replace 'Z' with '+00:00' to make it compatible
    return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc if not date_str.endswith('Z') else None)

