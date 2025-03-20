import pytz
from datetime import datetime

# Example of naive and aware datetime objects
naive_datetime = datetime.utcnow()  # naive datetime (no timezone info)
aware_datetime = datetime.utcnow().replace(tzinfo=pytz.utc)  # aware datetime (with UTC timezone)

# Check if the datetime is naive or aware
def check_if_aware(dt):
    if dt.tzinfo is None:
        print("This datetime is naive.")
    else:
        print("This datetime is aware.")

# Test with both naive and aware datetimes
check_if_aware(naive_datetime)  # This will print: This datetime is naive.
check_if_aware(aware_datetime)  # This will print: This datetime is aware.
