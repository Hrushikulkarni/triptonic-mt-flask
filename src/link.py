import pymongo
from utils import load_secrets
import random
import string

class MagicLink(object):
    mongo_connection_string = load_secrets()['MONGO_CONNECTION_STRING']
    mongo_client = pymongo.MongoClient(mongo_connection_string)
    mongo_db = mongo_client.get_database('TripTonicDump')
    mongo_collection = pymongo.collection.Collection(mongo_db, 'MagicLink')

    @staticmethod
    def generateLink():
        random_str = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=5))
        while MagicLink.mongo_collection.find_one({"link": random_str}):
            random_str = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=5))
        return random_str

    @staticmethod
    def save_trip(link, trip):
        MagicLink.mongo_collection.insert_one({"link": link, "trip": trip})

    @staticmethod
    def getTrip(link):
        res = MagicLink.mongo_collection.find_one({"link": link})
        return res["trip"] 
