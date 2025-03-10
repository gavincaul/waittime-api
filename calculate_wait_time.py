import math
import datetime
import requests
import json
from geopy.distance import geodesic
import random as rand
import numpy as np
from scipy.interpolate import CubicSpline



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
    time = datetime.datetime.now()
    day = time.weekday()

    if time.hour <= 10 and time.hour >= 1: # 1am to 10am its closed
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


def calculate_wait_time(lat,lon):

    time_factor = calculate_time_factor()
    if time_factor == "Deer Park is closed":
        return "Deer Park is closed"
    if time_factor == "No line":
        return "No line"
    
    d = distance_from_enterance(lat, lon)
    if d == "You are not in Deer Park":
        return 101010 # you are not in deer park

    time = (d / 2 - 5) * time_factor
    return time


print("Back of Deer Park:", calculate_wait_time(39.683360355019296, -75.75584360100328)) 
print("Mid way Point:", calculate_wait_time(39.683251985071145, -75.75583153106373)) 
print("Behind (middle) Deer Park:", calculate_wait_time(39.68338718945639, -75.75600855684388)) 
print()
print("to far right:", calculate_wait_time(39.68322205429359, -75.75568669178907))
print("to far left:", calculate_wait_time(39.683225150581585, -75.75652622316565))
print("to far top:", calculate_wait_time(39.68362719328449, -75.75609324484344))
print("to far bottom:", calculate_wait_time(39.68298984415029, -75.75595167701535))





