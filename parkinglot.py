#Campus Parking Lot Tracker
#----------------------------
# This file defines the ParkingLot class, which:
# - Stores parking lot data (name, spots, status, last update)
# - Manages a list of reports for this lot
# - Enforces anti-spam cooldown (10 min per user)
# - Updates status to majority vote when 3+ reports arrive in 15 min
# - Provides color for UI (green = AVAILABLE, yellow = LIMITED, red = FULL)

from collections import Counter
from datetime import datetime, timedelta
from report_model import Report

class ParkingLot:


    #Possible parking statuses - keep consistent with Report Class
    POSSIBLE_STATUSES = ["AVAILABLE", "LIMITED", "FULL"]

    def __init__(self, name, total_spots=None, current_status="AVAILABLE", last_updated=None): 

        self.name = name
        self.total_spots = total_spots
        self.current_status = current_status
        self.reports = [] #List of Report objects for this lot

        #Validation initial status
        if current_status not in self.POSSIBLE_STATUSES:
            raise ValueError(f"Invalid status: {self.current_status}. Must be one of the {self.POSSIBLE_STATUSES}. ")


        if last_updated is None:
            self.last_updated = datetime.now()
        else:
            self.last_updated = last_updated
        

    def get_status_color(self):
        # return "green" if AVAILABLE, "yellow" if LIMITED, "red" if FULL
        # or return None/invalid if unknown
        
        if self.current_status == "AVAILABLE":
            return "green"
        elif self.current_status == "LIMITED":
            return "yellow"
        elif self.current_status == "FULL":
            return "red"
        return None #Unknown status
    
    def can_user_report_again(self, user_id, cooldown_minutes=10):
        """
        Check if the given user is allowed to report again.
        Returns True if no report form this user in the last cooldown_minutes.
        
        """
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)

        for report in self.reports:
            if report.reporter == user_id:
                if report.timestamp >= cutoff_time:
                    return False
        return True
    
    def update_status_from_recent_reports(self, window_minutes=15):

        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_reports = []
    

        for report in self.reports:
            if report.timestamp >= cutoff_time:
                recent_reports.append(report)

        if len(recent_reports) < 3:
            return #Not enough votes
        
        status_counts = Counter(report.status for report in recent_reports)
        print(f"Status counts for {self.name}: {status_counts}") #Debug
        
        if status_counts:
            most_common_status, count = status_counts.most_common(1)[0]
            if count >= 3 and most_common_status != self.current_status:
                print(f"Updating {self.name} to {most_common_status} (majority {count} votes)")
                self.current_status = most_common_status   
                self.last_updated = datetime.now()

    """
    #Add a new report if the user is allowed (cooldown check).
    #Appends report and triggers majority vote check.
    Raise ValueError if user reported too recently.
    """
    def add_report(self, report):

        if not self.can_user_report_again(report.reporter):
            raise ValueError("You reported this lot too recently. Wait 10 minutes.")
        
        self.reports.append(report)
        self.update_status_from_recent_reports() 

    

    def __str__(self):
        # String representation for debuggin/printing. 
        time_str = self.last_updated.strftime("%I:%M %p")
        return f"{self.name}: {self.current_status} (last updated {time_str})"
    
if __name__ == "__main__":


    lot = ParkingLot("Create Lot:", total_spots=100, current_status="AVAILABLE")
    
    r = Report(lot, "AVAILABLE", "carlos")
    lot.add_report(r)
    print("After report", lot)
    print("Color:", lot.get_status_color())

    r2 = Report(lot, "FULL", "jose")
    try:
        lot.add_report(r2)
    except ValueError as e:
        print("Cooldown test:", e)