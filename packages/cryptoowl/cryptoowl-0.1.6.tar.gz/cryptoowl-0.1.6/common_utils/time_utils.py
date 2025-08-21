from datetime import datetime, timezone


def get_age_in_hrs_from_unix(unix_timestamp):
    try:
        if unix_timestamp:
            current_time = datetime.now()
            target_time = datetime.fromtimestamp(unix_timestamp)

            time_difference = current_time - target_time
            hours_from_now = time_difference.total_seconds() / 3600
            return hours_from_now
        else:
            return None
    except Exception as e:
        print(f"got error{e}")
        return None


def time_ago_from_timestamp_string(timestamp):
    try:
        now = datetime.now(timezone.utc)

        if isinstance(timestamp, str):
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            except ValueError:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        else:
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        # Calculate the difference between the current time and the given timestamp
        diff = now - dt

        # Convert the difference to minutes, hours, or days
        minutes = diff.total_seconds() // 60
        hours = diff.total_seconds() // 3600
        days = diff.days

        # Determine the appropriate time unit
        if days > 0:
            return f"{int(days)}d"
        elif hours > 0:
            return f"{int(hours)}h"
        elif minutes > 0:
            return f"{int(minutes)}m"
        else:
            return "just now"  # Less than a minute ago
    except Exception as e:
        print(f"Error @ time_ago_from_string :{e}")
        return ''


def format_datetime(input_date_string):
    input_format = "%Y-%m-%d %H:%M:%S"
    dt_object = datetime.strptime(str(input_date_string), input_format)
    return dt_object.strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_timestamp_to_datetime(timestamp):
    timestamp_str = str(timestamp)
    if len(timestamp_str) > 10:
        timestamp /= 1000

    return datetime.fromtimestamp(timestamp)