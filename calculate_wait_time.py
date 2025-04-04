import math
import datetime
import requests
import json
from geopy.distance import geodesic
import random as rand
import numpy as np
from scipy.interpolate import CubicSpline
import pytz



def calculate_weater_const(today_forecast):
    # output is ('This Afternoon', 'Mostly Sunny', 40, 'F', None)
    if today_forecast is None:
        return 1

    time = today_forecast["name"]
    weather = today_forecast["shortForecast"]
    temperature = today_forecast["temperature"]
    precipitation = today_forecast["probabilityOfPrecipitation"]['value']
    start_time = today_forecast["startTime"]
    end_time = today_forecast["endTime"]

    temp_penalty = 1
    if temperature < 50:
        temp_penalty = 0.5 + (temperature * 0.1)
    
    rain_penalty = 1
    if "rain" in weather.lower():
        rain_penalty = 0.5 + (precipitation * 0.01)

    total_penalty = (temp_penalty + rain_penalty)
        


def calculate_time_factor():
    eastern_time_zone = pytz.timezone('US/Eastern')
    time = datetime.datetime.now(eastern_time_zone)
    day = time.weekday()


    if time.hour < 10 and time.hour >= 1: # 1am to 10am its closed
        return "Deer Park is closed"

    if day <= 2: # Monday, Tuesday, Wednesday there's never a line 
        return 1
    

    factors_per_hour = {
        '3': {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35}, # Thursday
        '4': {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35}, # Friday
        '5': {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35}, # Saturday
        '6': {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35} # Sunday
        }
    
    x = np.array(list(factors_per_hour[str(day)].keys()))
    y = np.array(list(factors_per_hour[str(day)].values()))
    spline = CubicSpline(x, y)
    #sprint(time.minute)
    t = time.hour + time.minute / 60
    time_factor = spline(t)

    return time_factor

def distance_from_enterance(lat, long):
    '''
    top right 
    39.68338225968945, -75.7562183888234

    bottom left
    39.68307030354003, -75.75565931701483


    39.68311708340937, -75.75580418228357
    39.68311808340937, -75.75580418228357
    '''

    top_left = (39.68342700091772, -75.7562418910602)
    bottom_right = (39.683094707552556, -75.75568800693462)

    lat_ramp, lon_ramp = 39.683126300214155, -75.75582346055326

    if not ( long > top_left[1] and long < bottom_right[1] and lat < top_left[0] and lat > bottom_right[0]) :
        return "You are not in Deer Park"
    else:
        # Compute distance in feet
        distance_meters = geodesic((lat, long), (lat_ramp, lon_ramp)).meters
        distance_feet = distance_meters * 3.28084
        #print(f"D globe: {distance_feet:.2f} feet")
        

    # Approximate conversion factors
    feet_per_degree_lat = 364000  # 1 degree latitude ≈ 364,000 feet
    feet_per_degree_lon = 280000  # Approximate for 39.68° latitude

    # Calculate differences in latitude and longitude
    lat_diff = abs(lat_ramp - lat)
    lon_diff = abs(lon_ramp - long)

    # Convert differences to feet
    lat_diff_feet = lat_diff * feet_per_degree_lat
    lon_diff_feet = lon_diff * feet_per_degree_lon * math.cos(math.radians((lat_diff) / 2))

    # Total distance as the sum of lat and lon differences in feet
    distance_feet = lat_diff_feet + lon_diff_feet
    #print(f"D other: {distance_feet:.2f} feet")

        
    return distance_feet

def pseudo_prediction():

    eastern_time_zone = pytz.timezone('US/Eastern')
    current_time = datetime.datetime.now(eastern_time_zone)
    day = current_time.weekday()
    hour = current_time.hour


    wait_times = {
        (3, 18): (20, 30),  # Thursday, 6pm - 20-30 mins
        (3, 19): (25, 35),  # Thursday, 7pm - 25-35 mins
        (3, 20): (50, 75),  # Thursday, 8pm - 50-75 mins
        (3, 21): (60, 90),  # Thursday, 9pm - 60-90 mins
        (3, 22): (30, 40),  # Thursday, 10pm - 30-40 mins
        (3, 23): (10, 10),  # Thursday, 11pm - 10 mins
        (4, 18): (10, 10),  # Friday, 6pm - 10 mins
        (4, 19): (10, 20),  # Friday, 7pm - 10-20 mins
        (4, 20): (20, 35),  # Friday, 8pm - 20-35 mins
        (4, 21): (35, 55),  # Friday, 9pm - 35-55 mins
        (4, 22): (10, 10),  # Friday, 10pm - 10 mins
        (4, 23): (0, 0),    # Friday, 11pm - no wait
        (5, 18): (10, 10),  # Saturday, 6pm - 10 mins
        (5, 19): (10, 20),  # Saturday, 7pm - 10-20 mins
        (5, 20): (20, 35),  # Saturday, 8pm - 20-35 mins
        (5, 21): (35, 55),  # Saturday, 9pm - 35-55 mins
        (5, 22): (10, 10),  # Saturday, 10pm - 10 mins
        (5, 23): (0, 0),    # Saturday, 11pm - no wait
    }
    wait_time = wait_times.get((day, hour))
    
    if wait_time:
        return rand.randint(wait_time[0], wait_time[1])
    else:
        return 0


def calculate_wait_time(lat, lon):

    time_factor = calculate_time_factor()
    if time_factor == "Deer Park is closed":
        return 111111
    
    d = distance_from_enterance(lat, lon)
    if d == "You are not in Deer Park":
        return 101010 # you are not in deer park

    time = (d / 2 - 5) * time_factor
    return round(time)



def wait_time_prediction(lat, lon, minutes, timestamp):
    est = pytz.timezone('America/New_York')
    current_time = datetime.datetime.now(pytz.utc).astimezone(est)

    if timestamp.tzinfo is None:
        timestamp = pytz.utc.localize(timestamp) 
    timestamp_est = timestamp.astimezone(est)

    time_difference = (current_time - timestamp_est).total_seconds() / 60

    current_wait_time = calculate_wait_time(lat, lon)
    if time_difference < 0:
        return {"error": "Timestamp is in the future"}

    adjusted_wait_time = current_wait_time + (time_difference / 10)

    if current_wait_time <= minutes:
        adjusted_wait_time = current_wait_time + (minutes / 10)

    return {
        "predicted_wait_time": round(adjusted_wait_time),
    }




def calculate_wait_time_debug(lat, lon, min=None, hour=None, day=None):
    eastern_time_zone = pytz.timezone('US/Eastern')
    current_time = datetime.datetime.now(eastern_time_zone)

    # Use current time if min, hour, or day are not provided
    if day is None:
        day = current_time.weekday()
    if hour is None:
        hour = current_time.hour
    if min is None:
        min = current_time.minute

    # Calculate time factor based on the provided or current time
    factors_per_hour = {
        3: {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35},  # Thursday
        4: {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35},  # Friday
        5: {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35},  # Saturday
        6: {17: 1.25, 18: 1.35, 19: 1.45, 20: 1.55, 21: 1.55, 22: 1.45, 23: 1.35}   # Sunday
    }

    if day in factors_per_hour:
        x = np.array(list(factors_per_hour[day].keys()))
        y = np.array(list(factors_per_hour[day].values()))
        spline = CubicSpline(x, y)
        t = hour + min / 60
        time_factor = spline(t)
    else:
        time_factor = 1  
    if hour < 10 and hour >= 1:
        return {
            "code": 111111,
            "distance": 0,
            "time_factor": 0,
            "wait_time": 0,
            "day": day,
            "hour": hour,
            "minute": min,
            "message": "Deer Park is closed"
        }
    d = distance_from_enterance(lat, lon)
    if d == "You are not in Deer Park":
        return {
            "code": 101010,
            "distance": 0,
            "time_factor": 0,
            "wait_time": 0,
            "day": day,
            "hour": hour,
            "minute": min,
            "message": "You are not in Deer Park"
        }


    time = (d / 2 - 5) * time_factor

    return {
        "code": 200,
        "distance": round(d),
        "time_factor": time_factor,
        "wait_time": round(time),
        "day": day,
        "hour": hour,
        "minute": min
    }



def wait_time_prediction_debug(lat, lon, minutes=None, day=None, hour=None):

    eastern_time_zone = pytz.timezone('US/Eastern')
    current_time = datetime.datetime.now(eastern_time_zone)

    if day is None:
        day = current_time.weekday()
    if hour is None:
        hour = current_time.hour
    if minutes is None:
        minutes = current_time.minute


    current_wait_time = calculate_wait_time_debug(lat, lon, minutes, hour, day)

    if "error" in current_wait_time:
        return current_wait_time

    est = pytz.timezone('America/New_York')
    timestamp_est = datetime.datetime(
        current_time.year, current_time.month, current_time.day,
        hour, minutes, 0, tzinfo=est
    )

    time_difference = (current_time - timestamp_est).total_seconds() / 60

    if time_difference < 0:
        return {"error": "Timestamp is in the future"}

    adjusted_wait_time = current_wait_time["wait_time"] + (time_difference / 10)

    return {
        "predicted_wait_time": round(adjusted_wait_time),
        "current_wait_time": current_wait_time["wait_time"],
        "distance": current_wait_time["distance"],
        "time_factor": current_wait_time["time_factor"],
        "day": day,
        "hour": hour,
        "minute": minutes,
        "time_difference": round(time_difference, 2)
    }
def pseudo_prediction_debug(day, hour):



    wait_times = {
        (3, 18): (20, 30),  # Thursday, 6pm - 20-30 mins
        (3, 19): (25, 35),  # Thursday, 7pm - 25-35 mins
        (3, 20): (50, 75),  # Thursday, 8pm - 50-75 mins
        (3, 21): (60, 90),  # Thursday, 9pm - 60-90 mins
        (3, 22): (30, 40),  # Thursday, 10pm - 30-40 mins
        (3, 23): (10, 10),  # Thursday, 11pm - 10 mins
        (4, 18): (10, 10),  # Friday, 6pm - 10 mins
        (4, 19): (10, 20),  # Friday, 7pm - 10-20 mins
        (4, 20): (20, 35),  # Friday, 8pm - 20-35 mins
        (4, 21): (35, 55),  # Friday, 9pm - 35-55 mins
        (4, 22): (10, 10),  # Friday, 10pm - 10 mins
        (4, 23): (0, 0),    # Friday, 11pm - no wait
        (5, 18): (10, 10),  # Saturday, 6pm - 10 mins
        (5, 19): (10, 20),  # Saturday, 7pm - 10-20 mins
        (5, 20): (20, 35),  # Saturday, 8pm - 20-35 mins
        (5, 21): (35, 55),  # Saturday, 9pm - 35-55 mins
        (5, 22): (10, 10),  # Saturday, 10pm - 10 mins
        (5, 23): (0, 0),    # Saturday, 11pm - no wait
    }
    wait_time = wait_times.get((day, hour))
    
    if wait_time:
        return rand.randint(wait_time[0], wait_time[1])
    else:
        return 0





'''
    top left 
    39.68338225968945, -75.7562183888234

    bottom right
    39.68307030354003, -75.75565931701483


    if not ( long > top_left[1] and long < bottom_right[1] and lat < top_left[0] and lat > bottom_right[0]) :
        return "You are not in Deer Park"
'''
from unittest import TestCase

TestCase().assertEqual(calculate_wait_time(39.68350, -75.75650), 101010)  # Outside (top-right)
TestCase().assertEqual(calculate_wait_time(39.68290, -75.75500), 101010)  # Outside (bottom-left)
TestCase().assertEqual(calculate_wait_time(39.68360, -75.75570), 101010)  # Outside (above)
TestCase().assertEqual(calculate_wait_time(39.68310, -75.75630), 101010)  # Outside (left)
# 39.68320, -75.75590 -- inside
TestCase().assertEqual(calculate_wait_time_debug(39.68320, -75.75590, 0, 9, 1)["code"], 111111)  # Closed  
TestCase().assertEqual(calculate_wait_time_debug(39.68320, -75.75590, 0, 1, 1)["code"], 111111)  # Closed  
TestCase().assertEqual(calculate_wait_time_debug(39.68320, -75.75590, 0, 10, 1)["code"], 200)  # Open


wait_time = pseudo_prediction_debug(4, 18)  # Friday, 6pm
TestCase().assertGreaterEqual(wait_time, 10)
TestCase().assertLessEqual(wait_time, 30)

wait_time = pseudo_prediction_debug(3, 20)  # Thursday, 8pm
TestCase().assertGreaterEqual(wait_time, 60)
TestCase().assertLessEqual(wait_time, 90)

