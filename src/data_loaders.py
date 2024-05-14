import sys
import os
import requests
from flask import jsonify

# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.utils import load_secrets
from src.llm.agent import Agent
from src.engine import Engine

class DataLoader(object):
    def __init__(self, google_api_key):
        self.api_key = google_api_key
        self.secrets = load_secrets()

    def extract_params(self, query):
        travel_agent = Agent(google_gemini_key= self.secrets['GOOGLE_GEMINI_API_KEY'], debug=True)
        return travel_agent.validate_travel(query)
    
    def apply_filters(self, input):
        params = input
        input['location'] = input.get('location', '').replace(", ", '|')
        input['cuisine'] = input.get('cuisine', '').replace(", ", '|')

        places = {}
        places['restaurant'] = self.get_restaurants(input['cuisine'], input['location'])
        places['transit'] = self.get_transit(input['location'])
        places['tourist'] = self.get_tourist('', input['location'])

        #### TODO: save the result to cache

        filtered = Engine.filtering(places)
        flatData = Engine.covertFlat(filtered)

        results = {}
        results['places'] = flatData
        results['prompt'] = params
        return jsonify(results)
    
    def prompt(self, query):
        input = self.extract_params(query)
        return self.apply_filters(input)
    
    def places(self):
        pass

    def get_restaurants(self, cuisines, cities):
        try:
            query = f"{cuisines}+{cities}"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=restaurant&key={self.api_key}"

            response = requests.get(url)
            response_data = response.json()

            return response_data
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_tourist(self, neighborhood, cities):
        try:
            query = f"{neighborhood}+{cities}"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=tourist_attraction&key={self.api_key}"
            
            response = requests.get(url)
            response_data = response.json()

            return response_data

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_transit(self, cities):
        try:
            query = f"{cities}"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=transit_station&key={self.api_key}"
            
            response = requests.get(url)
            response_data = response.json()

            return response_data
        except Exception as e:
            return jsonify({'error': str(e)}), 500
