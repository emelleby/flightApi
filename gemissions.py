import requests
import os
# Lookup in the Google Travel API

def emissions(flights):
    key = os.environ['GOOGLE_API_KEY']
    url = f'https://travelimpactmodel.googleapis.com/v1/flights:computeFlightEmissions?key={key}'

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "flights": flights
    }

    # These are the flight instances
    # data = {
    #     "flights": [
    #         {
    #             "origin": "OSL",
    #             "destination": "CPH",
    #             "operatingCarrierCode": "SK",
    #             "flightNumber": 1469,
    #             "departureDate": {"year": 2024, "month": 9, "day": 29}
    #         },
    #         {
    #             "origin": "CPH",
    #             "destination": "ORD",
    #             "operatingCarrierCode": "SK",
    #             "flightNumber": 943,
    #             "departureDate": {"year": 2024, "month": 9, "day": 29}
    #         },

    #     ]
    # }



    response = requests.post(url, headers=headers, json=data)
    data = response.json()


    if response.status_code == 200:
        print('Response JSON:', response.json())
        # use the json library to pretty print the output
        # print(json.dumps(data['flightEmissions'], indent=4))

        econony = 0
        premiumEconomy = 0
        business = 0
        first = 0

        for emission in data['flightEmissions']:
            econony += emission["emissionsGramsPerPax"]["economy"]
            premiumEconomy += emission["emissionsGramsPerPax"]["premiumEconomy"]
            business += emission["emissionsGramsPerPax"]["business"]
            first += emission["emissionsGramsPerPax"]["first"]

        print(f"Economy: {econony/1000}kg")
        print(f"Premium Economy: {premiumEconomy/1000}kg")
        print(f"Business: {business/1000}kg")
        print(f"First: {first/1000}kg")

        return econony, premiumEconomy, business, first
    else:
        print(f"Failed to get data: {response.status_code}, {response.text}")
        return False