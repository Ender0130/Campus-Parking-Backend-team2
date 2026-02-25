from collections import Counter
from datetime import datetime, timedelta
# Future improvements:
# - Add validation for reporter (not empty/null)
# - Add method to check if report is recent (e.g. is_recent(minutes=15))
# - Serialize to JSON for database/API storage


class Report:

    # Note: reporter could be a username, UUID, or device ID in production
    def __init__(self, parking_lot, status, reporter,timestamp=None):
        
        if status not in ["AVAILABLE", "LIMITED", "FULL"]:
            raise ValueError(f"Invalid status: {status}. Must be one of AVAILABLE, LIMITED, FULL")

        self.parking_lot = parking_lot
        self.status = status
        self.reporter = reporter

        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp 
    

    def __str__(self):
        # Return a string like: "Report for [lot name]: [status] at [formatted time]"
        # Use strftime on timestamp for nice time like "08:15 PM"
        time_str = self.timestamp.strftime("%I:%M %p")
        return f"Report for {self.parking_lot.name}: {self.status} at {time_str} by user {self.reporter}"  