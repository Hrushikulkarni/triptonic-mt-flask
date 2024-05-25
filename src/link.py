import pymongo
from src.utils import load_secrets
import random
import string

class MagicLink(object):
    mongo_connection_string = load_secrets()['MONGO_CONNECTION_STRING']
    mongo_client = pymongo.MongoClient(mongo_connection_string)
    mongo_db = mongo_client.get_database('TripTonicDump')
    mongo_collection = pymongo.collection.Collection(mongo_db, 'MagicLink')

    @staticmethod
    def generate_link():
        random_str = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=5))
        while MagicLink.mongo_collection.find_one({"link": random_str}):
            random_str = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=5))
        return random_str

    @staticmethod
    def save_trip(link, name, params, places):
        MagicLink.mongo_collection.insert_one({"link": link, "places": places, "name": name, "params": params})

    @staticmethod
    def get_trip(link):
        res = MagicLink.mongo_collection.find_one({"link": link})
        return {
            "places": res['places'],
            "params": res['params'],
            "name": res['name']
        }
