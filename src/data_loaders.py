import sys
import os
import requests
from flask import jsonify
import pymongo


# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.llm.agent import Agent
from src.engine import Engine

class DataLoader(object):
    def __init__(self, maps_api_key, mongo_connection_string, gemini_api_key):
        self.gemini_api_key = gemini_api_key
        self.maps_api_key = maps_api_key
        print(mongo_connection_string)
        mongo_client = pymongo.MongoClient(mongo_connection_string)
        mongo_db = mongo_client.get_database('TripTonicDump')
        self.mongo_collection = pymongo.collection.Collection(mongo_db, 'GoogleMapsAPI')

    def extract_params(self, query):
        travel_agent = Agent(google_gemini_key= self.gemini_api_key, debug=True)
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
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=restaurant&key={self.maps_api_key}"

            response_data = self.mongo_collection.find_one({'url': url})
            if response_data is None:
                response = requests.get(url)
                response_data = response.json()
                self.mongo_collection.insert_one({'url': url, 'response': response_data})
            else:
                response_data = response_data['response']

            return response_data
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_tourist(self, neighborhood, cities):
        try:
            query = f"{neighborhood}+{cities}"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=tourist_attraction&key={self.maps_api_key}"
            
            response_data = self.mongo_collection.find_one({'url': url})
            if response_data is None:
                response = requests.get(url)
                response_data = response.json()
                self.mongo_collection.insert_one({'url': url, 'response': response_data})
            else:
                response_data = response_data['response']

            return response_data

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_transit(self, cities):
        try:
            query = f"{cities}"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=transit_station&key={self.maps_api_key}"
            
            response_data = self.mongo_collection.find_one({'url': url})
            if response_data is None:
                response = requests.get(url)
                response_data = response.json()
                self.mongo_collection.insert_one({'url': url, 'response': response_data})
            else:
                response_data = response_data['response']

            return response_data
        except Exception as e:
            return jsonify({'error': str(e)}), 500
