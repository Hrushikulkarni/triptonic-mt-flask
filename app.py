from flask import Flask, request, jsonify
import requests
from src.utils import load_secrets
from flask_cors import CORS, cross_origin
from src.data_loaders import DataLoader
from src.link import MagicLink

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
google_maps_key = load_secrets()['GOOGLE_MAPS_API_KEY']
wesbite_domain = load_secrets()['WEBSITE_DOMAIN']

secrets = load_secrets()

data_loader = DataLoader(maps_api_key=secrets['GOOGLE_MAPS_API_KEY'], 
                         mongo_connection_string=secrets['MONGO_CONNECTION_STRING'],
                         gemini_api_key=secrets['GOOGLE_GEMINI_API_KEY'])

@app.route("/hello")
@cross_origin()
def hello_world():
    return "Hello, World!"

@app.route('/prompt', methods=['POST'])
@cross_origin()
def prompt():
    import time
    try:
        tic = time.time()
        data = request.get_json()
        prompt_text = data.get('prompt')
        output = data_loader.prompt(prompt_text)
        tac = time.time()
        print("Time to process prompt: {}".format(round(tac - tic, 2)))
        return output
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/save', methods=['POST'])
@cross_origin()
def save_trip():
    try:
        data = request.get_json()
        places = data.get('places')
        name = data.get('name')
        params = data.get('params')
        link = wesbite_domain + MagicLink.generate_link()

        MagicLink.save_trip(link, name, params, places)
        return jsonify({"link": link})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_trip/<link>')
@cross_origin()
def get_trip(link):
    try:        
        return jsonify(MagicLink.get_trip(link))
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/extract_parameters', methods=['POST'])
@cross_origin()
def extract_parameters():
    try:
        data = request.get_json()
        prompt_text = data.get('prompt')
        input = data_loader.extract_params(prompt_text)
        return jsonify(input)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/apply_filters', methods=['POST'])
@cross_origin()
def apply_filters():
    try:
        input_filters = request.get_json()
        return data_loader.apply_filters(input_filters)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parameters', methods=['GET'])
@cross_origin()
def all_parameters():
    parameters = {
        'cuisines': [
            "Italian",
            "Indian",
            "Japanese",
            "Mexican",
            "French",
            "Chinese",
            "Korean",
        ],
        'mode_of_transports': ["Car", "Bus", "Trains", "Airplanes"],
        'type_of_trips': ["Family", "Friends", "Couples"],
        'attractions': ["Park", "Museums", "Clubs"]
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

# find routes        
# API  https://routes.googleapis.com/directions/v2:computeRoutes
@app.route('/maps/findroutes', methods=['POST'])
@cross_origin()
def findroutes():
    if request.method == 'POST':
        try:
            # google_maps_key = 'YOUR_API_KEY'  # Replace 'YOUR_API_KEY' with your actual API key

            payload = {
              
  "origin":{
    "location":{
      "latLng":{
        "latitude": 34.052235,
        "longitude": -118.243683
      }
    }
  },
  "destination":{
    "location":{
      "latLng":{
        "latitude": 37.773972,
        "longitude": -122.431297
      }
    }
  },
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE",
  "departureTime": "2024-10-15T15:01:23.045123456Z",
  "computeAlternativeRoutes": False,
  "routeModifiers": {
    "avoidTolls": False,
    "avoidHighways": False,
    "avoidFerries": False
  },
  "languageCode": "en-US",
  "units": "IMPERIAL"
}
            
            # Make the POST request using requests
            response = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes?key=AIzaSyDqIoSL0iKbpTakuGm2gHdvXGZyCxYj23Y', json=payload,     headers={'Content-Type': 'application/json',  'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'}
 )
            
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.text)

            routes_data = response.json().get('routes', [])
            routes = []
            for route_data in routes_data:
                route = {
                    'duration': route_data.get('legs', [{}])[0].get('duration', {}).get('text', ''),
                    'distance': route_data.get('legs', [{}])[0].get('distance', {}).get('value', 0),
                    'polyline': route_data.get('overview_polyline', {}).get('points', ''),
                }
                routes.append(route)

            return jsonify(routes)

        except Exception as e:
            # Handle errors
            print("Error:", e)
            return jsonify({'error': str(e)}), 500 

if __name__ == '__main__':
    app.run(port=5002)


