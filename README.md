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

2. Virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

3.Install dependencies
pip install flask flask-cors pytz

4.Run the API
python3 api.py

~Server starts on http://127.0.0.1:5001 (or your local network)

Example:
curl http://localhost:5001/lots

Sample Reponse:
[
 { 
   "name": "Parking Lot 1",
   "status": "AVAILABLE",
   "color" : "green,
   "last_updated": "07:08PM",
   "total_spots": 100
},
...
 ]

 
### How to add it now

1. In terminal (in your project folder):
2. Open 'README.md' in VS Code or any editor:
3. Paste the entire block above
4. Commit & push



 
