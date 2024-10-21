import json
import os

from functions import calc_distance_emissions, fetch_distance, handle_input, segments, sum_return
from lookup import FlightSegmentLookup
from gemissions import emissions

input = {
    "route":["BGO", "OSL"],
    "class":"economy",
    "return": 2,
    "rf": 2
}

def main(input):
  output = handle_input(input)
  flights = segments(output)
  # print(flights)
  flight_instances = []  # To store FlightSegmentLookup instances
  for i, flight in enumerate(flights):
    flight_name = f'flight{i+1}'
    # Create an instance of FlightSegmentLookup and assign it to a variable with the desired name
    globals()[flight_name] = FlightSegmentLookup(
        departure=flight[0]['departure'], arrival=flight[1]['arrival'])
    globals()[flight_name] = globals()[flight_name].find_flight()

    flight_instances.append(
        globals()[flight_name].to_dict())  # Store the instance

  # Now you can access the flights as flight1 and flight2
  # print(f'Flight: {flight1}')
  # print(type(flight2))
  # print(flight2)

  # Check the flight instances array
  # print(flight_instances)
  instances = []
  # Are there any flights found?
  for instance in flight_instances:
    if instance["flightNumber"]:
      print(f'Flight Number: {instance["flightNumber"]}')
      instances.append(instance)
    else:
      print("Not found")
  print(f'instances: {instances}')
  # If there is a flight or two that has not been found, calculate emissions based on distance
  
  return instances
  # return flight_instances # Return the list of flight instances if needed


if __name__ == "__main__":
  # main(input)

  get_flights = main(input)
  print(json.dumps(get_flights, indent=4))
  sum_return(get_flights, input)


