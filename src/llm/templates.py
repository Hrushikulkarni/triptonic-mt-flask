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

class TripParameters(BaseModel):
    latitude: float = Field(description="Latitude coordinate of the location")
    longitude: float = Field(description="Longitude coordinate of the location")
    location: str = Field(description="Comma separated locations list in the trip")
    duration: int = Field(description="Duration of the trip in days")
    origin: str = Field(description="Starting point of the trip")
    no_of_people: int = Field(description="Number of people involved in the trip")
    mode_of_transport: str = Field(description="Mode of transport such as car, train, bus, airplane")
    type_of_trip: str = Field(description="Trip type such as family, couple")
    cuisine: str = Field(description="Based on the food items mentioned, infer cuisine.")
    budget: float = Field(description="Total budget of the entire trip")
    timings: str = Field(description="Daily timings for travel")
    attraction: str = Field(description="Tourist attractions like museums, national parks, historical places, etc.")

class ValidationTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. Determine if the user's
            request is reasonable and achievable within the constraints they set.

            A valid request should contain the following:
            - Few locations, should mention at least one
            - A trip duration that is reasonable given the location(s), can be number of days
            - Mode of transport
            - Number of people involved in the trip
            - Some other details, like the type of trip such as family/couple
            - Some cuisine inferred from a food item

            Any request that contains potentially harmful activities is not valid, regardless of what
            other details are provided.

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

class ValidationTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. Determine if the user's
            request is reasonable and achievable within the constraints they set.

            A valid request should contain the following:
            - Few locations, should mention at least one
            - A trip duration that is reasonable given the location(s), can be number of days
            - Mode of transport
            - Number of people involved in the trip
            - Some other details, like the type of trip such as family/couple
            - Some cuisine inferred from a food item

            Any request that contains potentially harmful activities is not valid, regardless of what
            other details are provided.

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

class ValidateFilteringTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. Determine if the user's
            request is reasonable and achievable within the constraints they set.

           Your output should be valid if it contains: 
            - the longitude and lattitude coordinated of the restaurant or tourist place.
            - the longitudeDelta and latitudeDelta.
            - the icon of the place.
            - the name of the place
            - the visiting time of the place and the day of the trip when the user should visit that location.
            - the budget for visiting that place.

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
            - Starting point of the trip should be present
            - A trip duration that is reasonable given the location(s), can be number of days
            - Mode of transport
            - Number of people involved in the trip
            - Some other details, like the type of trip such as family/couple
            - Some cuisine inferred from a food item

            Your output should always contain a list of locations separated by comma, at least one. 
            It may contain the type of trip like family, couple, friends.
            It may contain the trip duration in days.
            It may contain the number of people involved in the trip.
            It may contain mode of transport which can be either car, train, bus, airplane. If you can't infer the mode of transit, make a best guess given the trip location or the budget.
            It may contain a food item, from which you can infer cuisine or directly the cuisine will be mentioned.
            It may contain attractions like museums, national parks, clubs, historical places, etc.

            For example:

            ####
            Plan a two day trip from Irvine to San Diego. It should be for seven people.
            You can consider Mexican and Indian cuisine and it is a Friends road trip. Wish to explore the pizza places! Would like to cafe hop along the way with unlimited budget with travel starting from 9AM to 6 PM daily .
            #####

            Output:
            {{  
                "location": "San Diego",
                "origin" : "Irvine",
                "duration": 2,
                "no_of_people": 7,
                "budget": unlimited,
                "mode_of_transport": "car",
                "type_of_trip": "friends",
                "cuisine": "mexican, indian",
                "timings": "9:00-18:00",
                "attractions": "cafe"
            }}

            In the example above "mexican" and "indian" are cuisines, not a location.
            One observation is that places with suffix is usually not a actuall location.
            and cuisines will come some word like "cuisine" and "food", don't consider them as location.

            mode_of_transport can be only one of the following options: "car", "train", "bus", "airplane".
            type_of_trip can be only one of the following options: "family", "friends", "couple".
            these values should all be in lowercase.

            timings will be a range of time in HH:MM 24Hr format.
            
            origin stores the starting point of the trip.

            For rest of the parameters, make the best guess based on the trip location and other parameters.

            the ouput must contain every parameter: location, origin, duration, no_of_people, mode_of_transport, type_of_trip, cuisine, attractions
            and it must not be null, have these default values:
            mode_of_transports: car
            type_of_trips: family
            attractions: park
            cuisines: italian
            no_of_people: 2
            budget: 500
            duration: 2
            timings: 9:00-20:00


            Also, if in prompt, food items like pizza or pasta is mentioned then it's cuisine will be "italian", not pizza and pasta
            similar is sushi is mentioned, then it's cuisine will be japanese.
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

class FilteringTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. This request should be valid.

            A valid request should contain the following:
            - Location of the trip
            - A trip duration that is reasonable given the location(s), can be number of days
            - Budget of the trip
            - Daily timings of travel
            - Origin of the trip
            - Mode of transport
            - Number of people involved in the trip
            - Some other details, like the type of trip such as family/couple
            - Some cuisine inferred from a food item

            Your output should always contain a list of locations separated by comma, at least one. 
            It may contain the longitude and lattitude coordinated of the restaurant or tourist place.
            It may contain the longitudeDelta and latitudeDelta.
            It may contain the icon of the place.
            It may contain the name of the place
            It may contain the visiting time of the place and the day of the trip when the user should visit that location.
            It may contain the budget for visiting that place.

            For example:

            ####
            'location': 'Irvine', 'origin': 'Los Angeles', 'duration': 2, 'no_of_people': 5, 'budget': 'tight', 'mode_of_transport': 'car', 'type_of_trip': 'family', 'cuisine': 'italian', 'timings': '06:00-17:00', 'attractions': 'historical places'
            #####

            Output:
            [
                {{
                    "latitude": 33.670339,
                    "longitude": -117.788647,
                    "latitudeDelta": 1,
                    "longitudeDelta": 1,
                    "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/restaurant-71.png",
                    "name": "California Pizza Kitchen at Alton Square",
                    "time": "4:00 PM",
                    "budget": 50,
                    "day": 1
                    
                }}
            ]



            latitude and longitude should be the lattitude and longitude coordinates of the location of the individual place in name.

            budget is the cost of visiting that place.

            name is the name of that tourist spot/ restaurant.

            time is the time of arrival. day refers to the day of the trip when the user should visit this place. photos contains the images of that place, height and width contain the height and width of the image.

            html attributions contains the google maps link of the place along with a photo reference.

            the ouput must contain every parameter: latitude, longitude, latitudeDelta, longitudeDelta, icon, name, time, day, budget.

            time should be in HH:MM format and day should be numeric.

            Also, latitude and longitude should be of the google maps location of the place.
        """

        self.human_template = """
            ####{query}####
        """

        self.parser = PydanticOutputParser(pydantic_object=Validation)
        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )


