from flask import Flask, request, jsonify
from calculate_wait_time import calculate_wait_time  # Import your function

app = Flask(__name__)

@app.route('/calculate-wait-time', methods=['GET'])
def get_wait_time():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Missing coordinates"}), 400

    result = calculate_wait_time(lat, lon)
    return jsonify({"wait_time": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 