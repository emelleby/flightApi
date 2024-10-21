import json
import math
import requests
import time

from datetime import date, timedelta

from gemissions import emissions

def get_tomorrow_date():
    now = time.localtime()
    searchdate = time.strftime("%Y-%m-%d", now)
    print("Today's date:", searchdate)

    # Extract year, month, and day as integers
    year = int(searchdate[:4])
    month = int(searchdate[5:7])
    day = int(searchdate[8:])

    # Create a date object
    today = date(year, month, day)

    # Calculate tomorrow's date
    tomorrow = today + timedelta(days=1)

    # Extract year, month, and day from tomorrow's date, formatting with leading zeros
    # tomorrow_year = str(tomorrow.year)
    # tomorrow_month = str(tomorrow.month).zfill(2)  # Add leading zero if needed
    # tomorrow_day = str(tomorrow.day).zfill(2)   # Add leading zero if needed

    # print("Tomorrow's date:", tomorrow.strftime("%Y-%m-%d"))
    # print("Year:", tomorrow_year)
    # print("Month:", tomorrow_month)
    # print("Day:", tomorrow_day)

    return tomorrow

def handle_input(input):
  if len(input["route"]) == 2:
      return [input["route"]]
  else:
      return [input["route"][:2], [input["route"][1], input["route"][2]]]

def segments(route):
    flights = []
    if len(route) == 1:
        flights.append([{"departure": route[0][0]}, {"arrival": route[0][1]}])
        return flights

    else:
        for i in range(len(route)):
            flights.append([{"departure": route[i][0]}, {"arrival": route[i][1]}])
        return flights

# print(segments(route))

def fetch_distance(departure, arrival):

  url = "https://airportgap.com/api/airports/distance"
  headers = {
      'Content-Type': 'application/json'
  }

  #The data variable should be a dictionary
  data = {
      "from": departure,
      "to": arrival
  }

  response = requests.post(url, headers=headers, json=data)
  data = response.json()
  return int(round(data["data"]["attributes"]["kilometers"]))

# print(fetch_distance("OSL","CPH"))
# print(fetch_distance("OSL","ORD"))

# print(json.dumps(fetch_distance("OSL","CPH"), indent=4))

def calc_distance_emissions(route, fare_class, return_type, rf):
  factors = {
    "short": {
      "average": 0.175,
      "economy": 0.175,
      "premiumEconomy": 0.18,
      "business": 0.18,
      "first": 0.185
    },
    "medium": {
      "average": 0.135,
      "economy": 0.12,
      "premiumEconomy": 0.12,
      "business": 0.195,
      "first": 0.195
    },
    "long": {
      "average": 0.095,
      "economy": 0.08,
      "premiumEconomy": 0.125,
      "business": 0.215,
      "first": 0.305
    }
  }
  print("Calculation", route, fare_class, return_type, rf)
  co2e = 0
  if len(route) == 2:
    departure = route[0]
    arrival = route[1]
    distance = fetch_distance(departure, arrival)
    print(f'Distance: {distance}km from {departure} to {arrival}')
    if distance < 600:
      print(f"Short distance: {distance}km")
      co2e = factors["short"][fare_class] * distance * return_type * rf
    elif distance < 1500:
      print(f"Medium distance: {distance}km")
      co2e = factors["medium"][fare_class] * distance * return_type * rf
    else:
      print(f"Long distance: {distance}km")
      co2e = factors["long"][fare_class] * distance * return_type * rf

  elif len(route) == 3:
    co2e = 0
    for i in range(len(route) -1):
        departure = route[i]
        arrival = route[i + 1]
        distance = fetch_distance(departure, arrival)
        print(f'Distance: {distance}km from {departure} to {arrival}')
        if distance < 600:
            print(f"Short distance: {distance}km")
            co2e += factors["short"][fare_class] * distance * return_type * rf  #updated
        elif distance < 1500:
            print(f"Medium distance: {distance}km")
            co2e += factors["medium"][fare_class] * distance * return_type * rf  #updated
        else:
            print(f"Long distance: {distance}km")
            co2e += factors["long"][fare_class] * distance * return_type * rf  #updated

    print(f'Emissions: {co2e:.2f}kg')  #updated


  print(f'Emissions: {co2e:.2f}kg')

  return co2e

def sum_return(get_flights, input):
  # Check how many flights are found
  # If 2 flights are found, calculate emissions from Google for both
  if len(get_flights) == 2:
    print("Found 2 flights")
    # Get Emissions from Google
    co2e = emissions(get_flights)
    # Select the correct emission value based on input["class"]
    if input["class"] == "average":
      selected_emission = co2e[0] + (co2e[2] + 0.1)
    elif input["class"] == "economy":
      selected_emission = co2e[0]
    elif input["class"] == "premiumEconomy":
      selected_emission = co2e[1]
    elif input["class"] == "business":
      selected_emission = co2e[2]
    elif input["class"] == "first":
      selected_emission = co2e[3]
    else:
      selected_emission = None  # Handle invalid class input
    if selected_emission is not None:
      print(f'Emissions len_2: {(selected_emission * input["rf"] * input["return"]) / 1000:.2f}kg')
      return (selected_emission * input["rf"] * input["return"]) / 1000  # Convert to kg and return
    else:
      print("Invalid fare class.")
      # Perhaps return an error message or raise an exception


  # If 1 flight is found, calculate emissions from Google for that flight
  elif len(get_flights) == 1:
    print("Found 1 flight")
    distance_co2e = 0
    # Find the flight that was not found if any
    print(type(input["route"]))
    print(input["route"])
    if len(input["route"]) == 3:
      if get_flights[0]["origin"] == input["route"][0]:
        new_route = [input["route"][1], input["route"][2]]
      else:
        new_route = [input["route"][0], input["route"][1]]
    # Calculate that based on distance
      distance_co2e = calc_distance_emissions(new_route, input["class"], input["return"], input["rf"])
      print(f'New_route: {new_route} Distance_emissions: {distance_co2e}kg')
    
  # Add the 2 calculations together and return the total emissions
    # Get Emissions from Google
    co2e = emissions(get_flights)
    # Select the correct emission value based on input["class"]
    if input["class"] == "average":
      selected_emission = co2e[0] + (co2e[2] + 0.1)
    elif input["class"] == "economy":
      selected_emission = co2e[0]
    elif input["class"] == "premiumEconomy":
      selected_emission = co2e[1]
    elif input["class"] == "business":
      selected_emission = co2e[2]
    elif input["class"] == "first":
      selected_emission = co2e[3]
    else:
      selected_emission = None  # Handle invalid class input
    if selected_emission is not None:
      print(f'Emissions_len 1: {((selected_emission / 1000) * input["return"] * input["rf"]) + distance_co2e:.2f}kg')
      return ((selected_emission / 1000) * input["return"] * input["rf"]) + distance_co2e  # Convert to kg and return
      
    else:
      print("Invalid fare class.")
      # Perhaps return an error message or raise an exception

  # If none where found, calculate both based on distance and return the total emissions
  else:
    print("No flights found")
    co2e = calc_distance_emissions(input["route"], input["class"], input["return"]), input["rf"]
    print(f'Emissions_len 0: {co2e:.2f}kg')
    return co2e / 1000  # Convert to kg and return

  # Get Emissions from Google
  # co2e = emissions(get_flights)

  print(f'Economy: {(co2e[0]/1000) * input["rf"]}kg')
  print(f'Premium Economy: {(co2e[1]/1000) * input["rf"]}kg')
  print(f'Business: {(co2e[2]/1000) * input["rf"]}kg')
  print(f'First: {(co2e[3]/1000) * input["rf"]}kg')
