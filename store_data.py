from pymongo import MongoClient
import os
from datetime import datetime, timedelta
def store_data(lat, lon, timestamp, wait_time):
    mongo_uri = os.environ.get('MONGO_URI')
    if mongo_uri:
        client = MongoClient(mongo_uri)
        
        db = client["deerparkline"]
        collection = db["deerparklineprediction"]
        
        new_location_data = {
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.utcnow(),
            "wait_time": wait_time
        }

        collection.insert_one(new_location_data)
        
def get_data():
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        return 404

    client = MongoClient(mongo_uri)
    db = client["deerparkline"]
    collection = db["deerparklineprediction"]
    
    latest_entries = list(collection.find().sort("timestamp", -1).limit(10))

    if not latest_entries:
        return 404


    two_hours_ago = datetime.utcnow() - timedelta(hours=2)


    valid_entries = [
        entry for entry in latest_entries
        if entry['timestamp'] >= two_hours_ago
    ]

    if not valid_entries:
        return 404

    longest_entry = max(valid_entries, key=lambda x: x['wait_time'])

    lat = longest_entry['latitude']
    lon = longest_entry['longitude']
    minutes = longest_entry['wait_time']
    timestamp = longest_entry['timestamp']

    return [lat, lon, minutes, timestamp]
