import spacy
import requests
from spacy.matcher import PhraseMatcher

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")


def processPrompt(strInput):
    print(strInput)
    def train_food():
        food_items = ["pizza", "pasta", "burger", "sushi", "salad", "taco"]

        # Create a PhraseMatcher object and add the food item patterns to it
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(food) for food in food_items]
        matcher.add("FOOD_ITEMS", patterns)
        return matcher

    def extract_cities(text):
        # Process the text with spaCy
        doc = nlp(text)
        
        # Extract entities identified as GPE (Geo-Political Entities)
        cities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        
        return cities

    def extract_food_items(text):
        doc = nlp(text)
        matches = matcher(doc)
        # Extract matched food items
        food_items_found = [doc[start:end].text for match_id, start, end in matches]
        return food_items_found

    matcher = train_food()
    # sentence = "I had pizza and salad for dinner last night, and I'm thinking of having sushi for lunch today."
    food_items = extract_food_items(strInput)
    print("Food items mentioned:", food_items)

    # sentence = "I have visited Los Angeles."
    cities = extract_cities(strInput)
    print("Cities mentioned:", cities)

    url = "http://127.0.0.1:5002"

    if len(food_items) == 0:
        data = {
        "city": cities[0]
        }

        response = requests.post(url + "/maps/tourist", json=data)

    # Print response from server (optional)
        if response.status_code == 200:
            print("Success:", response.json())
            return response.json()
        else:
            print("Error:", response.status_code, response.text)

    else:
        data = {
        "city": cities[0],
        "category": food_items[0]
        }

        response = requests.post(url + "/maps/restaurants", json=data)

    # Print response from server (optional)
        if response.status_code == 200:
            print("Success:", response.json())
            return response.json()
        else:
            print("Error:", response.status_code, response.text)

# processPrompt('Went to New York for a pizza.')