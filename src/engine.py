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
    food_items = extract_food_items(strInput)
    print("Food items mentioned:", food_items)
    cities = extract_cities(strInput)
    print("Cities mentioned:", cities)

    url = "http://127.0.0.1:5002"
    combined_response = {}

    if cities:
        city = cities[0]  # Assuming we're only interested in the first city mentioned
        tourist_data = {"city": city}
        tourist_response = requests.post(url + "/maps/tourist", json=tourist_data)
        if tourist_response.status_code == 200:
            print("Tourist Info Success:", tourist_response.json())
            combined_response["tourist"] = tourist_response.json()
        else:
            print("Tourist Info Error:", tourist_response.status_code, tourist_response.text)

        transit_data = {"city": city}
        transit_response = requests.post(url + "/maps/transit", json=transit_data)
        if transit_response.status_code == 200:
            print("Transit Info Success:", transit_response.json())
            combined_response["transit"] = transit_response.json()
        else:
            print("Transit Info Error:", transit_response.status_code, transit_response.text)

        if food_items:
            restaurant_data = {
                "city": city,
                "category": food_items[0]
            }
            restaurant_response = requests.post(url + "/maps/restaurants", json=restaurant_data)
            if restaurant_response.status_code == 200:
                print("Restaurant Info Success:", restaurant_response.json())
                combined_response["restaurant"] = restaurant_response.json()
            else:
                print("Restaurant Info Error:", restaurant_response.status_code, restaurant_response.text)

    return combined_response