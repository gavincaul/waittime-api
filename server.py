from flask import Flask, request, jsonify
import threading
from calculate_wait_time import calculate_wait_time, wait_time_prediction, pseudo_prediction
from store_data import store_data, get_data
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/calculate-wait-time', methods=['GET'])
def get_wait_time():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Missing coordinates"}), 400
    result = calculate_wait_time(lat, lon)

    response = jsonify({"wait_time": result})
    threading.Thread(target=store_data_in_background, args=(lat, lon, result)).start()

    return response


def store_data_in_background(lat, lon, wait_time):
    timestamp = datetime.utcnow()  
    store_data(lat, lon, timestamp, wait_time)

@app.route('/predict-wait-time', methods=['GET'])
def predict_wait_time():
    get_data_result = get_data()
    if get_data_result == 404:
        return jsonify({"pseudo_prediction": pseudo_prediction()}), 404
    else:
        return jsonify({"wait_time_prediction": wait_time_prediction(get_data_result[0], get_data_result[1], get_data_result[2], get_data_result[3])})


if __name__ == "__main__":
    app.run(debug=True)
