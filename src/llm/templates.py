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
    location: str = Field(description="Comma separated locations list in the trip")
    duration: str = Field(description="Duration of the trip in days")
    no_of_people: str = Field(description="Number of people involved in the trip")
    mode_of_transport: str = Field(description="Mode of transport such as car, train, bus, airplane")
    type_of_trip: str = Field(description="Trip type such as family, couple")
    cuisine: str = Field(description='Based on the food items mentioned, infer cuisine.')
    attraction: str = Field(description='Can be tourist attractions like museums, national parks, historical places, etc.')

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

class ExtractParametersTemplate(object):
    def __init__(self):
        self.system_template = """
            You are a travel agent who helps users make exciting travel plans.

            The user's request will be denoted by four hashtags. This request should be valid.

            A valid request should contain the following:
            - Few locations, should mention at least one
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
            You can consider Mexican and Indian cuisine and it is a Friends road trip. Wish to explore the Pizza places! Would like to Cafe hop along the way.
            #####

            Output:
            {{
                "location": "Irvine, Los Angeles",
                "duration": 2,
                "no_of_people": 7,
                "mode_of_transport": "car",
                "type_of_trip": "friends",
                "cuisine": "Italian",
                "attractions": "Cafe"
            }}

            mode_of_transport can be only one of the following options: "car", "train", "bus", "airplane".
            type_of_trip can be only one of the following options: "family", "friends", "couple".
            For rest of the parameters, make the best guess based on the trip location and other parameters.
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
