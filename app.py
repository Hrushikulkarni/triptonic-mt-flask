from flask import Flask, request, jsonify
import requests
from src.utils import load_secrets
from flask_cors import CORS, cross_origin
from src.data_loaders import DataLoader

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
google_maps_key = load_secrets()['GOOGLE_MAPS_API_KEY']

data_loader = DataLoader(google_api_key=load_secrets()['GOOGLE_MAPS_API_KEY'])

@app.route("/hello")
@cross_origin()
def hello_world():
    return "Hello, World!"

@app.route('/prompt', methods=['POST'])
@cross_origin()
def prompt():
    try:
        data = request.get_json()
        prompt_text = data.get('prompt')
        return data_loader.prompt(prompt_text)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/userinput', methods=['POST'])
@cross_origin()
def user_input():
    try:
        data = request.get_json()
        prompt_text = data.get('prompt')
        input = data_loader.get_input(prompt_text)
        return jsonify(input)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/parameters', methods=['GET'])
@cross_origin()
def all_parameters():
    parameters = {
        'cuisines': [
            "🍕Italian",
            "🍛Indian",
            "🍜Japanese",
            "🌮Mexican",
            "🍟French",
            "🍖Chinese",
            "🍙Korean",
        ],
        'mode_of_transports': ["🚗 Car", "🚌 Bus", "🚂 Trains", "🛩️ Airplanes"],
        'type_of_trips': ["🧑‍🧑‍🧒‍🧒 Family", "👯 Friends", "👩‍❤️‍👨 Couples"],
        'attractions': ["🎢 Park", "🦖 Museums", "🕺🏻 Clubs"]
    }

    return jsonify(parameters)

@app.route('/maps/restaurants', methods=['POST'])
@cross_origin()
def mresto():
    try:
        data = request.get_json()
        # neighborhood = data.get('neighborhood')
        city = data.get('city')
        category = data.get('category')
        # neighborhood = ''
        # city = 'Irvine'
        # category = ''
        
        # Constructing the query URL
        query = f"{category}+{city}"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=restaurant&key={google_maps_key}"
        
        # Making the GET request to the Google Places API
        response = requests.get(url)
        response_data = response.json()
        
        # Logging and returning the data
        print(response_data)
        return jsonify(response_data)
    except Exception as e:
        # Handling errors
        return jsonify({'error': str(e)}), 500

@app.route('/maps/tourist', methods=['POST'])
@cross_origin()
def tourism():
    try:
        data = request.get_json()
        # neighborhood = data.get('neighborhood')
        city = data.get('city')
        neighborhood = ''
        # city = 'Irvine|Los Angeles'
        
        # Constructing the query URL
        query = f"{neighborhood}+{city}"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=tourist_attraction&key={google_maps_key}"
        
        # Making the GET request to the Google Places API
        response = requests.get(url)
        response_data = response.json()
        
        # Logging and returning the data
        print(response_data)
        return jsonify(response_data)
    except Exception as e:
        # Handling errors
        return jsonify({'error': str(e)}), 500
    
@app.route('/maps/transit', methods=['POST'])
@cross_origin()
def transit():
    try:
        data = request.get_json()
        # neighborhood = data.get('neighborhood')
        city = data.get('city')
        # neighborhood = 'UCI'
        # city = 'Irvine'
        
        # Constructing the query URL
        query = f"{city}"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=transit_station&key={google_maps_key}"
        
        # Making the GET request to the Google Places API
        response = requests.get(url)
        response_data = response.json()
        
        # Logging and returning the data
        print(response_data)
        return jsonify(response_data)
    except Exception as e:
        # Handling errors
        return jsonify({'error': str(e)}), 500

@app.route('/maps/route/drive', methods=['POST'])
@cross_origin()
def route():
    try:
        data = request.get_json()
        origin_address = data.get("origin", {}).get("address", "")
        destination_address = data.get("destination", {}).get("address", "")
        compute_alternative_routes = data.get("computeAlternativeRoutes", True)
        
        # Construct the payload for the Google Directions API request
        api_payload = {
            "origin": origin_address,
            "destination": destination_address,
            "alternatives": compute_alternative_routes,
            "travelMode": data.get("travelMode"),
            "routingPreference": data.get("routingPreference")
        }
        url = "https://maps.googleapis.com/maps/api/directions/json"
        
        # Making the GET request to the Google Directions API
        response = requests.get(url, params={**api_payload, "key": google_maps_key})
        response_data = response.json()
        
        # Logging and returning the data
        print(response_data)
        return jsonify(response_data)
    except Exception as e:
        # Handling errors
        return jsonify({'error': str(e)}), 500

######################TODO
@app.route('/maps/route/transit', methods=['POST'])
@cross_origin()
def route_transit():
    try:
        data = request.get_json()
        origin_address = data.get("origin", {}).get("address", "")
        destination_address = data.get("destination", {}).get("address", "")
        travel_mode = data.get("travelMode", "TRANSIT")
        compute_alternative_routes = data.get("computeAlternativeRoutes", True)
        transit_preferences = data.get("transitPreferences", {})
        
        # Construct the payload for the Google Directions API request
        api_payload = {
            "origin": origin_address,
            "destination": destination_address,
            "mode": travel_mode.lower(),
            "alternatives": compute_alternative_routes,
            "transit_mode": transit_preferences.get("allowedTravelModes", ["train"]),
            "transit_routing_preference": transit_preferences.get("routingPreference", "less_walking")
        }
        
        url = "https://maps.googleapis.com/maps/api/directions/json"
        
        # Making the GET request to the Google Directions API
        response = requests.get(url, params={**api_payload, "key": google_maps_key})
        response_data = response.json()
        
        # Logging and returning the data
        print(response_data)
        return jsonify(response_data)
    except Exception as e:
        # Handling errors
        return jsonify({'error': str(e)}), 500
    

@app.route('/maps/textsearch', methods=['POST'])
@cross_origin()
def textsearch():
    if request.method == 'POST':
        try:
            # Parse JSON payload from request
            payload = {
                'textQuery': 'Spicy Vegetarian Food in Irvine, CA'
            }

            # Set up the headers for the POST request
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': google_maps_key,  # Replace 'YOUR_google_maps_key' with your actual API key
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel'
            }

            # Make the POST request using requests
            response = requests.post('https://places.googleapis.com/v1/places:searchText', json=payload, headers=headers)

            # Process the response
            print(response.json())
            return jsonify(response.json())
        except Exception as e:
            # Handle errors
            return jsonify({'error': str(e)}), 500

@app.route('/maps/nearsearch', methods=['POST'])
@cross_origin()
def nearsearch():
    if request.method == 'POST':
        try:
            # Define the payload for the POST request
            payload = {
                'includedTypes': ['tourist_attraction'],
                'rankPreference': 'DISTANCE',
                'maxResultCount': 10,
                'locationRestriction': {
                    'circle': {
                        'center': {
                            'latitude': 33.669445,
                            'longitude': -117.823059
                        },
                        'radius': 5000.0
                    }
                }
            }

            # Set up the headers for the POST request
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': google_maps_key,  # Replace 'YOUR_google_maps_key' with your actual API key
                'X-Goog-FieldMask': 'places.displayName'
            }

            # Make the POST request using requests
            response = requests.post('https://places.googleapis.com/v1/places:searchNearby', json=payload, headers=headers)

            # Process the response
            print(response.json())
            return jsonify(response.json())
        except Exception as e:
            # Handle errors
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5002)
