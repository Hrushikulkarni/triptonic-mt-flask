from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Validation(BaseModel):
    plan_is_valid: str = Field(
        description="This field is 'yes' if the plan is feasible, 'no' otherwise"
    )

class ValidationTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. Determine if the user's
            request is reasonable and achievable within the constraints they set.

            A valid request should contain the following:
            - Few locations, should mention at least one

            For example you are supposed to set plan_is_valid = 0 for all the requests not pertaining to a travel request.
            Additionally for unreasonable requests like "Fly me to the moon" or "I want to walk from India to USA" set plan_is_valid = 0 
            If the request is not valid, set
            plan_is_valid = 0

            If the request seems reasonable, then set plan_is_valid = 1.

            {format_instructions}
        """

        self.human_template = """
            ####{query}####
        """

        self.parser = PydanticOutputParser(pydantic_object=Validation)

        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )

class ExtractParametersTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. This request should be valid.

            A valid request should contain the following:
            - Few locations the user want to visit, should mention at least one
            - If origin as in the start of the location is not provided by the user, consider one of the location(s) of the trip as the origin. It should be a single location only.
            - A trip duration that is reasonable given the location(s), can be number of days
            - Mode of transport
            - Number of people involved in the trip
            - Some other details, like the type of trip such as family/couple/friends
            - Some cuisine inferred from a food item or any activity the user would want to do
            - Distance radius within which the user wishes to travel in miles, default it to 50.

            Your output should always contain a list of locations separated by comma, at least one. 
            It may contain the type of trip like family, couple, friends.
            It may contain the trip duration in days.
            It may contain the number of people involved in the trip.
            It may contain mode of transport which can be either "DRIVING", "BICYCLING", "WALKING" and "TRANSIT". If you can't infer the mode of transit, make a best guess given the trip location or the budget, but always give any of the above values only.

            It may contain a food item, from which you can infer cuisine or directly the cuisine will be mentioned.
            It may contain attractions like museums, national parks, clubs, historical places, give the values like park, museum, club (any of these values).

            For example:

            ####
            Plan a two day trip from Irvine to San Diego. It should be for seven people.
            You can consider Mexican and Indian cuisine and it is a Friends road trip. Wish to explore the pizza places! Would like to cafe hop along the way with unlimited budget with travel starting from 9AM to 6 PM daily .
            #####

            Output:
            {{  
                "location": "San Diego, Irvine",
                "origin" : "Irvine",
                "duration": 2,
                "no_of_people": 7,
                "budget": unlimited,
                "mode_of_transport": "car",
                "type_of_trip": "friends",
                "cuisine": "mexican, indian",
                "timings": "9:00-18:00",
                "attractions": "cafe",
                "distance": 50
            }}

            In the example above "mexican" and "indian" are cuisines, not a location.
            One observation is that places with suffix is usually not a actuall location.
            and cuisines will come some word like "cuisine" and "food", don't consider them as location.

            budget would have any of the following values - low, medium, high. Consider default value as "medium"

            mode_of_transport can be only one of the following options: "DRIVING", "BICYCLING", "WALKING" and "TRANSIT", these values should all be in uppercase.

            type_of_trip can be only one of the following options: "family", "friends", "couple".
            these values should all be in lowercase.

            timings will be a range of time in HH:MM 24Hr format.
            
            origin stores the starting point of the trip, if origin is not provided, consider one of the location as origin. DO NOT, I REPEAT DO NOT send null or None origin.

            For rest of the parameters, make the best guess based on the trip location and other parameters.

            the output must contain every parameter: location, origin, duration, no_of_people, mode_of_transport, type_of_trip, cuisine, attractions, distance
            and it must not be null, have these default values:
            mode_of_transports: car
            type_of_trips: friends
            attractions: cafe
            cuisine: indian
            no_of_people: 2
            budget: medium
            duration: 2
            timings: 9:00-20:00
            distance: 50


            Also, if in prompt, food items like pizza or pasta is mentioned then it's cuisine will be "italian", not pizza and pasta
            similarly if sushi is mentioned, then it's cuisine will be japanese.
            Also consider contextual cues like "reading manga" to be japanese cuisine and stuff like that.
        """

        self.human_template = """
            ####{query}####
        """

        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )

class FilterAndOrderingTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. It will have a list of JSON objects indicating details about the places and another parameter object that you will use to filter and order to create the perfect itinerary.

            Consider below rules to do the FILTERING of the list of JSON objects:
            - Maintain exact number of places based on the trip "duration":
                One day trip: 5 places
                Two day trip: 9 places
                Three day trip: 12 places and so on
            - Per day atleast 2 "tourist" type places should be present.
            - Include all of the type "tourist", "restaurant" and "transit".
            - The total count of "transit" type places should not exceed the count of "tourist" type places.
            - Select places suitable for the "mode_of_transport":
                WALKING/BIKING: Choose close-by places or those with bike lanes.
                DRIVING: Include places that can be farther apart.
                TRANSIT: Ensure places are near transit locations.
            - Match the "description" of places with the "attractions" in the parameters.
            - Match the "description" of places with the "type_of_trip" in the parameters.
            - Select restaurants/tourist places based on the "price_range" suitable for the "type_of_trip".

            Consider below rules to do the ORDERING of the list of JSON objects:
            - Plan an itinerary for a day trip that includes at least two "tourist" type places. If it's a two-day trip, include at least four "tourist" type places, and so on.
            - Make sure that the number of "tourist" type places is more than the number of "transit" and "restaurant" type places.
            - No more than 5 places in total per day and no 2 locations at a same time of the day.
            
            Finally you have to add two attributes to the place's JSON object, they are:
            "day": 1 (it is a number)
            "time": "14:00" (it is in 24 hour format)
            The rules to add these attributes are:
            - Based on the "duration" attribute in the parameter object passed by the user, distribute the places from the JSON object list that we have ordered so far into specific days and give an ideal time to visit that place. Ensure that the day attribute value is less than the "duration" and the time is in 24 hour format.

            For example for the user prompt below:
            I am providing the minified JSON in this example
            ####
            [{{"business_status":"OPERATIONAL","description":"Small, cozy dinner spot with framed photos covering the walls serving classic Italian comfort food.","id":"ChIJ8TFl3M0sDogRlO3_4QWlWVE","latitude":41.891066,"latitudeDelta":1,"longitude":-87.6468314,"longitudeDelta":1,"name":"La Scarola","notes":"Notes...","price_range":2,"rating":4.7,"serves":["lunch"],"todays_working_hours":"4:00 AM - 10:00 PM","total_reviews":1687,"type":"tourist","website":"http://www.lascarola.com/"}},{{"business_status":"OPERATIONAL","description":"Small, cozy dinner spot with framed photos covering the walls serving classic Italian comfort food.","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png","id":"ChIJ8TFl3M0sDogRlO3_4QWlWVE","latitude":41.891066,"latitudeDelta":1,"longitude":-87.6468314,"longitudeDelta":1,"name":"La Scarola","notes":"Notes...","price_range":2,"rating":4.7,"serves":[],"todays_working_hours":"4:00 AM - 10:00 PM","total_reviews":1687,"type":"restaurent","website":"http://www.lascarola.com/"}},{{"business_status":"OPERATIONAL","description":"","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/generic_business-71.png","id":"ChIJr9gxmVLTD4gR3ZORqBIh9jo","latitude":41.8967801,"latitudeDelta":1,"longitude":-87.6279205,"longitudeDelta":1,"name":"Chicago","notes":"Notes...","price_range":2,"rating":4.2,"serves":[],"todays_working_hours":"10:00 AM - 06:00 PM","total_reviews":77,"type":"transit","website":""}},{{"business_status":"OPERATIONAL","description":"","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/generic_business-71.png","id":"ChIJr9gxmVLTD4gR3ZORqBIh9jo","latitude":41.8967801,"latitudeDelta":1,"longitude":-87.6279205,"longitudeDelta":1,"name":"Chicago","notes":"Notes...","price_range":2,"rating":4.2,"serves":[],"todays_working_hours":"10:00 AM - 06:00 PM","total_reviews":77,"type":"tourist","website":""}},{{"business_status":"OPERATIONAL","description":"Relaxed, stylish restaurant & bar near the United Center featuring upscale Italian-American cuisine.","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png","id":"ChIJvS_32SYtDogR2UwKCEiOpw0","latitude":41.8815596,"latitudeDelta":1,"longitude":-87.65316159999999,"longitudeDelta":1,"name":"Viaggio Restaurant Chicago","notes":"Notes...","price_range":2,"rating":4.7,"serves":["lunch"],"todays_working_hours":"4:00 AM - 9:00 PM","total_reviews":748,"type":"tourist","website":"https://www.viaggiochicago.com/"}}]
            PARAMETER {{
                "attractions": "cafe",
                "budget": "medium",
                "cuisine": "italian",
                "distance": 50,
                "duration": 2,
                "location": "Chicago",
                "mode_of_transport": "DRIVING",
                "no_of_people": 2,
                "origin": "Chicago",
                "timings": "9:00-20:00",
                "type_of_trip": "friends"
            }}
            #####

            Output:
            [{{"day":1,"business_status":"OPERATIONAL","description":"Relaxed, stylish restaurant & bar near the United Center featuring upscale Italian-American cuisine.","id":"ChIJvS_32SYtDogR2UwKCEiOpw0","latitude":41.8815596,"latitudeDelta":1,"longitude":-87.65316159999999,"longitudeDelta":1,"name":"Viaggio Restaurant Chicago","notes":"Notes...","price_range":2,"rating":4.7,"serves":["lunch"],"todays_working_hours":"4:00 AM - 9:00 PM","total_reviews":748,"type":"tourist","website":"https://www.viaggiochicago.com/","time":"13:30"}},{{"day":2,"business_status":"OPERATIONAL","description":"","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/generic_business-71.png","id":"ChIJr9gxmVLTD4gR3ZORqBIh9jo","latitude":41.8967801,"latitudeDelta":1,"longitude":-87.6279205,"longitudeDelta":1,"name":"Chicago","notes":"Notes...","price_range":2,"rating":4.2,"serves":[],"todays_working_hours":"10:00 AM - 06:00 PM","total_reviews":77,"type":"transit","website":"","time":"11:00"}},{{"day":2,"business_status":"OPERATIONAL","description":"Small, cozy dinner spot with framed photos covering the walls serving classic Italian comfort food.","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png","id":"ChIJ8TFl3M0sDogRlO3_4QWlWVE","latitude":41.891066,"latitudeDelta":1,"longitude":-87.6468314,"longitudeDelta":1,"name":"La Scarola","notes":"Notes...","price_range":2,"rating":4.7,"serves":["dinner"],"todays_working_hours":"4:00 AM - 10:00 PM","total_reviews":1687,"type":"restaurant","website":"http://www.lascarola.com/","time":"15:00"}},{{"day":2,"business_status":"OPERATIONAL","description":"","icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/generic_business-71.png","id":"ChIJr9gxmVLTD4gR3ZORqBIh9jo","latitude":41.8967801,"latitudeDelta":1,"longitude":-87.6279205,"longitudeDelta":1,"name":"Chicago","notes":"Notes...","price_range":2,"rating":4.2,"serves":[],"todays_working_hours":"10:00 AM - 06:00 PM","total_reviews":77,"type":"tourist","website":"","time":"18:00"}}]
            
            Day and time must be added in the generated JSON keeping all other fields as it is.
            Output JSON should be also minified version of JSON.
            Without fail ensure your output is a list of JSON objects having all the previous fields and the two newly added fields for "day" and "time". Ensure property names have double quotes and not single quotes. Ensure that the number of objects in the JSON list do not go below 5 for the generated trip.
        """

        self.human_template = """
            ####{query}####
        """

        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )
