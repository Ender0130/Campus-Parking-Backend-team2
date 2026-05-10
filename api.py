from flask import Flask, jsonify, request
from flask_cors import CORS
from parkinglot import ParkingLot
from report_model import Report

app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------------
# In-memory user store — replace with a database later
# -------------------------------------------------------------------
users = {}  # { username: password }

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    if username in users:
        return jsonify({"success": False, "error": "Username already taken"}), 409

    users[username] = password
    return jsonify({"success": True, "username": username})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if users.get(username) == password:
        return jsonify({"success": True, "username": username})
    return jsonify({"success": False, "error": "Invalid username or password"}), 401

# -------------------------------------------------------------------
# Multi-campus data setup
# -------------------------------------------------------------------
CAMPUS_LOT_CONFIG = {
    "SDSU": [
        {"name": "Parking Lot 1", "total_spots": 100},
        {"name": "Parking Lot 2B", "total_spots": 100},
        {"name": "Parking Lot 2C", "total_spots": 100},
        {"name": "Parking Lot 3", "total_spots": 100},
        {"name": "Parking Lot 4", "total_spots": 100},
        {"name": "Parking Lot 12", "total_spots": 100},
        {"name": "Parking Lot 15", "total_spots": 100},
        {"name": "Parking Lot 17", "total_spots": 100},
        {"name": "Parking Lot 17A", "total_spots": 100},
        {"name": "Parking Lot 17B", "total_spots": 100},
    ],
    "UCSD": [
        {"name": "Gilman Parking Structure", "total_spots": 250},
        {"name": "Hopkins Parking Structure", "total_spots": 200},
        {"name": "Pangea Parking Structure", "total_spots": 300},
    ],
    "CSUSM": [
        {"name": "Lot B", "total_spots": 120},
        {"name": "Lot C", "total_spots": 140},
        {"name": "Parking Structure 1", "total_spots": 220},
    ]
}


def build_lots_by_campus():
    lots_by_campus = {}

    for campus_name, campus_lots in CAMPUS_LOT_CONFIG.items():
        lots_by_campus[campus_name] = {}

        for lot_data in campus_lots:
            lot_name = lot_data["name"]
            total_spots = lot_data.get("total_spots", 100)

            lots_by_campus[campus_name][lot_name] = ParkingLot(
                name=lot_name,
                campus=campus_name,
                total_spots=total_spots
            )

    return lots_by_campus


lots_by_campus = build_lots_by_campus()

user_points = {}
VIEW_COST = 1
REPORT_REWARD = 5
STARTING_POINTS = 0

def get_points(reporter):
    if reporter not in user_points:
        user_points[reporter] = STARTING_POINTS
    return user_points[reporter]


def get_or_create_campus(campus_name):
    if campus_name not in lots_by_campus:
        lots_by_campus[campus_name] = {}
    return lots_by_campus[campus_name]


def get_or_create_lot(campus_name, lot_name):
    campus_lots = get_or_create_campus(campus_name)

    if lot_name not in campus_lots:
        campus_lots[lot_name] = ParkingLot(
            name=lot_name,
            campus=campus_name,
            total_spots=100
        )

    return campus_lots[lot_name]


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.route('/campuses', methods=['GET'])
def get_campuses():
    return jsonify(sorted(list(lots_by_campus.keys())))


@app.route('/lots', methods=['GET'])
def get_lots():
    campus_name = request.args.get('campus', 'SDSU')
    reporter = request.args.get('reporter', 'anonymous')

    if campus_name not in lots_by_campus:
        return jsonify({
            "success": False,
            "error": f"Campus '{campus_name}' not found"
        }), 404

    points = get_points(reporter)

    if points < VIEW_COST:
        return jsonify({
            "success": False,
            "error": "Not enough points. Submit a report to view parking data.",
            "points": points
        }), 403

    user_points[reporter] -= VIEW_COST

    campus_lots = lots_by_campus[campus_name]

    return jsonify({
        "success": True,
        "points": user_points[reporter],
        "lots": [lot.to_dict() for lot in campus_lots.values()]
    })
    return jsonify([lot.to_dict() for lot in campus_lots.values()])


@app.route('/report', methods=['POST'])
def submit_report():
    data = request.get_json() or {}

    campus_name = data.get('campus', 'SDSU')
    lot_name = data.get('lot_name')
    status = data.get('status')
    reporter = data.get('reporter')

    if not lot_name or not status or not reporter:
        return jsonify({
            "success": False,
            "error": "Missing lot_name, status, or reporter"
        }), 400

    try:
        lot = get_or_create_lot(campus_name, lot_name)
        report = Report(lot, status, reporter)
        lot.add_report(report)
        get_points(reporter)
        user_points[reporter] += REPORT_REWARD

        return jsonify({
            "success": True,
            "campus": campus_name,
            "points": user_points[reporter],
            "lot": lot.to_dict()
        })  
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/debug/all-lots', methods=['GET'])
def get_all_lots():
    return jsonify({
        campus_name: [lot.to_dict() for lot in campus_lots.values()]
        for campus_name, campus_lots in lots_by_campus.items()
    })


if __name__ == '__main__':
    total_lots = sum(len(campus_lots) for campus_lots in lots_by_campus.values())
    print(
        f"API started with {len(lots_by_campus)} campuses "
        f"and {total_lots} pre-loaded lots"
    )
    app.run(debug=True, port=5001, host='0.0.0.0')