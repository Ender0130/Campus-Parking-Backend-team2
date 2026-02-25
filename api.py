from flask import Flask, jsonify, request
from flask_cors import CORS
from parkinglot import ParkingLot
from report_model import Report
import pytz

app = Flask(__name__)
CORS(app)

# Pre-load your lots
lots = {}
lot_names = [
    "Parking Lot 1", "Parking Lot 2B", "Parking Lot 2C",
    "Parking Lot 3", "Parking Lot 4", "Parking Lot 12", "Parking Lot 15",
    "Parking Lot 17", "Parking Lot 17A", "Parking Lot 17B"
]

for name in lot_names:
    lots[name] = ParkingLot(name, total_spots=100)

@app.route('/lots', methods=['GET'])
def get_lots():
    tz = pytz.timezone('America/Los_Angeles')
    return jsonify([
        {
            "name": lot.name,
            "status": lot.current_status,
            "color": lot.get_status_color(),
            "last_updated": lot.last_updated.isoformat(),
            "total_spots": lot.total_spots or 0
        } for lot in lots.values()
    ])

@app.route('/report', methods=['POST'])
def submit_report():
    data = request.json
    lot_name = data.get('lot_name')
    status = data.get('status')
    reporter = data.get('reporter')

    if not lot_name or not status or not reporter:
        return jsonify({"success": False, "error": "Missing lot_name, status, or reporter"}), 400

    if lot_name not in lots:
        lots[lot_name] = ParkingLot(lot_name)

    lot = lots[lot_name]
    r = Report(lot, status, reporter)

    try:
        lot.add_report(r)
        tz = pytz.timezone('America/Los_Angeles')
        return jsonify({
            "success": True,
            "status": lot.current_status,
            "color": lot.get_status_color(),
            "last_updated": lot.last_updated.isoformat(),
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    print(f"API started with {len(lots)} pre-loaded lots")
    app.run(debug=True, port=5001, host='0.0.0.0')