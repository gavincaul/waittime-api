from pymongo import MongoClient, errors
import os
from datetime import datetime, timedelta
import pytz


def get_est_time():
    est_tz = pytz.timezone('US/Eastern')  
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc) 
    est_time = utc_time.astimezone(est_tz)  
    return est_time

def store_data(lat, lon, timestamp, wait_time):
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        print("Error: MongoDB URI not set.")
        return
    
    try:

        with MongoClient(mongo_uri) as client:
            db = client["deerparkline"]
            collection = db["deerparklineprediction"]
            est_time = get_est_time()
            new_location_data = {
                "latitude": lat,
                "longitude": lon,
                "timestamp": est_time,
                "wait_time": wait_time
            }
            collection.insert_one(new_location_data)
            print("Data stored successfully.")
    except errors.PyMongoError as e:
        print(f"Error storing data: {e}")

def get_data():
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        print("Error: MongoDB URI not set.")
        return 404

    try:

        with MongoClient(mongo_uri) as client:
            db = client["deerparkline"]
            collection = db["deerparklineprediction"]
            
            latest_entries = list(collection.find().sort("timestamp", -1).limit(10))

            if not latest_entries:
                print("No data found in the collection.")
                return 100001



            two_hours_ago = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(hours=2)
            valid_entries = [
                entry for entry in latest_entries
                if entry['timestamp'].astimezone(pytz.utc) >= two_hours_ago
            ]

            if not valid_entries:
                print("No valid data within the last 2 hours.")
                return 100001

            longest_entry = max(valid_entries, key=lambda x: x['wait_time'])

            lat = longest_entry['latitude']
            lon = longest_entry['longitude']
            minutes = longest_entry['wait_time']
            timestamp = longest_entry['timestamp']

            return [lat, lon, minutes, timestamp]
    except errors.PyMongoError as e:
        print(f"Error retrieving data: {e}")
        return 404

get_data()