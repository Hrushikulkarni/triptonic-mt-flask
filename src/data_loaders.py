import sys
import os
import requests
from flask import jsonify
import pymongo
import concurrent.futures
from .utils import get_top_n_places, clean_google_maps_data, calculate_minmax_score, stats_printer

# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.agent import Agent, enrich_params
from src.engine import Engine

class DataLoader(object):
    def __init__(self, maps_api_key, mongo_connection_string, gemini_api_key):
        self.gemini_api_key = gemini_api_key
        self.maps_api_key = maps_api_key
        mongo_client = pymongo.MongoClient(mongo_connection_string)
        mongo_db = mongo_client.get_database('TripTonicDump')
        self.gmaps_collection = pymongo.collection.Collection(mongo_db, 'GoogleMapsAPI')
        self.places_collection = pymongo.collection.Collection(mongo_db, 'PlacesCache')
        self.llm_collection = pymongo.collection.Collection(mongo_db, 'LLMCache')
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
        self.engine = Engine()

    def extract_params(self, query):
        travel_agent = Agent(google_gemini_key=self.gemini_api_key, debug=True)
        return travel_agent.validate_travel(query)
    
    def apply_filters(self, input):
        params = input
        input['location'] = input.get('location', '').replace(", ", '|')
        input['cuisine'] = input.get('cuisine', '').replace(", ", '|')
        input['budget'] = input.get('budget', '')
        input['timings'] = input.get('timings', '')
        input['origin'] = input.get('origin', '')

        input = enrich_params(input)
        res = self.llm_collection.find_one({'input': input})

        if res is None:
            import time
            tic = time.time()
            places = {} 
            places['restaurant'] = clean_google_maps_data('restaurant', self.get_restaurants(input['cuisine'], input['location']))
            places['transit'] = clean_google_maps_data('transit', calculate_minmax_score(self.get_transit(input['location'])[:10]))
            places['tourist'] = clean_google_maps_data('tourist', self.get_tourist('', input['location']))
            tac = time.time()
            print('Total restaurants:', len(places['restaurant']))
            print('Total transits:', len(places['transit']))
            print('Total tourists:', len(places['tourist']))
            print("Time to fetch places: {}".format(round(tac - tic, 2)))
            data = self.engine.filter(places, input)
            print('After filtering length:', len(data))
            stats_printer(data)
            data = self.engine.order(data, input)
            print('After ordering length:', len(data))
            stats_printer(data)
            res = {'input': input, 'data': data}
            self.llm_collection.insert_one(res)

        results = {}
        results['places'] = res['data']
        results['prompt'] = params
        return jsonify(results)
    
    def prompt(self, query):
        input = self.extract_params(query)
        return self.apply_filters(input)
    
    def places(self):
        pass

    def get_place_details(self, place):
        place_id = place.get('place_id')
        response_data = self.places_collection.find_one({'place_id': place_id})
        if response_data is None:
            fields = 'current_opening_hours,serves_breakfast,serves_lunch,serves_brunch,serves_dinner,editorial_summary,website'
            url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={self.maps_api_key}"
            response = requests.get(url)
            details = response.json().get('result', {})
            enriched_place = { **place, **details }
            self.places_collection.insert_one({**enriched_place})
            return enriched_place
        return response_data

    def get_restaurants(self, cuisines, cities):
        query = f"{cuisines}+{cities}"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=restaurant&key={self.maps_api_key}"
        document = self.gmaps_collection.find_one({'url': url})
        if document is None:
            response = requests.get(url)
            response_data = response.json()
            results = response_data.get('results', [])

            # Filter for top 10 results here only
            results = get_top_n_places(10, results)

            detailed_places = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.get_place_details, place) for place in results]
                for future in concurrent.futures.as_completed(futures):
                    fields_data = future.result()
                    detailed_places.append(fields_data)
            self.gmaps_collection.insert_one({'url': url, 'response': detailed_places})
            return detailed_places
        return document['response']

    def get_tourist(self, neighborhood, cities):
        query = f"{neighborhood}+{cities}"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=tourist_attraction&key={self.maps_api_key}"
        document = self.gmaps_collection.find_one({'url': url})
        if document is None:
            response = requests.get(url)
            response_data = response.json()
            results = response_data.get('results', [])

            # Filter for top 10 results here only
            results = get_top_n_places(10, results)

            detailed_places = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.get_place_details, place) for place in results]
                for future in concurrent.futures.as_completed(futures):
                    fields_data = future.result()
                    detailed_places.append(fields_data)
            self.gmaps_collection.insert_one({'url': url, 'response': detailed_places})
            return detailed_places
        return document['response']

    def get_transit(self, cities):
        try:
            query = f"{cities}"
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&type=transit_station&key={self.maps_api_key}"
            
            response_data = self.gmaps_collection.find_one({'url': url})
            if response_data is None:
                response = requests.get(url)
                response_data = response.json()
                response_data = response_data.get('results', [])
                self.gmaps_collection.insert_one({'url': url, 'response': response_data})
            else:
                response_data = response_data['response']

            return response_data
        except Exception as e:
            return jsonify({'error': str(e)}), 500
