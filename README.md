# Campus Parking Backend API

Flask-based backend for the Campus Park mobile app. Tracks parking lot availability using crowdsourced reports from students. Features anti-spam cooldown (10 min per user) and majority-vote status updates (3+ reports in 15 min).

## Features
- Pre-loaded parking lots with default "AVAILABLE" status
- Report submission with user-level cooldown
- Majority vote logic to update lot status
- PST time formatting for last_updated
- CORS enabled for React Native front-end

## Tech Stack
- Python 3.13
- Flask (API server)
- pytz (timezone handling for San Diego/PST)
- Custom classes: `ParkingLot` & `Report`

## Setup & Run

1. Clone the repo
   ```bash
   git clone https://github.com/devbycarlos/campus-parking-backend.git
   cd campus-parking-backend
