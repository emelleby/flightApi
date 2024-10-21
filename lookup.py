import time
import requests
import os

from dataclasses import dataclass
from functions import get_tomorrow_date

@dataclass
class FlightSegmentLookup:

    departure: str
    arrival: str
    flightnumber: str = ""
    date: str = ""
    year: str = ""
    month: str = ""
    day: str = ""

    def find_flight(self):
        now = time.localtime()
        searchdate = time.strftime("%Y-%m-%d", now)
        # Set the date to search to tomorrow 
        self.date = str(get_tomorrow_date())
        start_time = 1
        end_time = 12
        # Replace 'your_api_key_here' with your actual MagicAPI key

        API_KEY = os.environ['MAGIC_API_KEY']
        # url = f'https://api.magicapi.dev/api/v1/aedbx/aerodatabox/flights/airports/Iata/{self.departure}/{self.date}T{str(start_time).zfill(2)}%3A00/{self.date}T{str(end_time)}%3A00'

        headers = {
            'accept': 'application/json',
            'x-magicapi-key': API_KEY
        }

        params = {
            'direction': 'Departure',
            'withLeg': 'false',
            'withCancelled': 'true',
            'withCodeshared': 'true',
            'withCargo': 'false',
            'withPrivate': 'false',
            'withLocation': 'false'
        }
        # First try to look up within the next 12 hours. If it fails try the following 12 hours.
        try:
            for i in range(2):
                url = f'https://api.magicapi.dev/api/v1/aedbx/aerodatabox/flights/airports/Iata/{self.departure}/{self.date}T{str(start_time).zfill(2)}%3A00/{self.date}T{str(end_time)}%3A00'
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()  # Raise an exception for bad status codes

                data = response.json()

                for departure in data["departures"]:
                    # Check if the necessary keys exist before accessing them
                    if "movement" in departure and "airport" in departure["movement"] and "iata" in departure["movement"]["airport"] and departure["movement"]["airport"]["iata"] == self.arrival:
                        # print(departure["movement"]["airport"]["iata"])
                        self.flightnumber = departure["number"].replace(" ", "")
                        date = departure["movement"]["scheduledTime"]["local"][:10]
                        self.date = date
                        self.year = date[:4]
                        self.month = date[5:7]
                        self.day = date[8:10]
                        # Returns one flight if found. ELSE it will return the object as is.
                        return self

                print("Nothing found in the first lookup. Trying to shift time and call again.")
                # Shift time 12 hours
                start_time = start_time + 11
                end_time = end_time + 11

            return self

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the API request: {e}")

    def to_dict(self):
        """Returns the flight information in the desired dictionary format."""
        return {
            "origin": self.departure,
            "destination": self.arrival,
            "operatingCarrierCode": self.flightnumber[:2] if self.flightnumber else "", # Extract airline code if available
            "flightNumber": int(self.flightnumber[2:]) if self.flightnumber else "", # Extract flight number if available
            "departureDate": {
                "year": int(self.year) if self.year else "",
                "month": int(self.month) if self.month else "",
                "day": int(self.day) if self.day else ""
            }
        }
