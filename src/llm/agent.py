import json
from langchain.chains import LLMChain, SequentialChain
from langchain_google_genai import GoogleGenerativeAI
from .templates import (
    FilterAndOrderingTemplate,
    ValidationTemplate,
    ExtractParametersTemplate
)

import logging
import time

logging.basicConfig(level=logging.INFO)

def enrich_params(params):
    print('Enriching params:', params)
    if params.get('origin') is None:
        params['origin'] = params['location'].split(', ')[0]
    if params.get('timings', '') == '':
        params['timings'] = '07:00-20:00'

    if params.get('distance') is None:
        params['distance'] = 20
    else:
        params['distance'] = int(params['distance'])
    
    if params.get('no_of_people') is None:
        params['no_of_people'] = 2
    else:
        params['no_of_people'] = int(params['no_of_people'])
    
    if params.get('duration') is None:
        params['duration'] = 2
    else:
        params['duration'] = int(params['duration'])
    
    if params.get('budget') is None:
        params['budget'] = 'medium'

    if params.get('mode_of_transport') is None:
        params['mode_of_transport'] = 'DRIVING'
    elif params.get('mode_of_transport') == 'BIKING':
        params['mode_of_transport'] = 'BICYCLING'

    params['mode_of_transport'] = 'DRIVING'
    if params.get('budget') == 'low':
        if params.get('no_of_people') <= 1:
            params['mode_of_transport'] = 'WALKING'
        elif params.get('no_of_people') < 4:
            params['mode_of_transport'] = 'BIKING'
    if params.get('budget') == 'medium':
        if params.get('no_of_people') <= 4:
            params['mode_of_transport'] = 'TRANSIT'
    
    print('Enriched params:', params)
    return params

class Agent(object):
    def __init__(
        self,
        google_gemini_key,
        model= 'gemini-1.0-pro-latest',
        temperature=0,
        debug=True,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._openai_key = google_gemini_key

        self.chat_model = GoogleGenerativeAI(model=model, temperature=temperature, google_api_key=self._openai_key)
        self.validation_prompt = ValidationTemplate()
        self.extract_parameters_prompt = ExtractParametersTemplate()
        self.generate_trip_prompt = FilterAndOrderingTemplate()
        self.validation_chain = self._set_up_validation_chain(debug)
        self.generate_trip_chain = self._set_up_generate_trip_chain(debug)

    def _set_up_generate_trip_chain(self, debug=True):
        travel_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.generate_trip_prompt.chat_prompt,
            verbose=debug,
            output_key="agent_suggestion",
        )
        overall_chain = SequentialChain(
            chains=[travel_agent],
            input_variables=["query"],
            output_variables=["agent_suggestion"],
            verbose=debug,
        )

        return overall_chain        

    def _set_up_validation_chain(self, debug=True):
      
        # make validation agent chain
        validation_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.validation_prompt.chat_prompt,
            output_parser=self.validation_prompt.parser,
            output_key="validation_output",
            verbose=debug,
        )

        travel_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.extract_parameters_prompt.chat_prompt,
            verbose=debug,
            output_key="agent_suggestion",
        )
        
        # add to sequential chain 
        overall_chain = SequentialChain(
            chains=[validation_agent, travel_agent],
            input_variables=["query", "format_instructions"],
            output_variables=["validation_output","agent_suggestion"],
            verbose=debug,
        )

        return overall_chain

    def generate_trip(self, query):
        t1 = time.time()
        self.logger.info(
            "Calling Generate Trip (model is {}) on user input".format(
                self.chat_model.model
            )
        )
        response = self.generate_trip_chain(
            {
                "query": query,
            }
        )
        trip = response["agent_suggestion"]
        print('### START')
        trip = trip.strip().replace("'", '"')
        print(trip)
        print('### END')
        t2 = time.time()
        output = json.loads(trip)
        self.logger.info("Time to generate trip request: {}".format(round(t2 - t1, 2)))

        return output

    def validate_travel(self, query):
        self.logger.info("Validating query")
        t1 = time.time()
        self.logger.info(
            "Calling validation (model is {}) on user input".format(
                self.chat_model.model
            )
        )
        validation_result = self.validation_chain(
            {
                "query": query,
                "format_instructions": self.validation_prompt.parser.get_format_instructions(),
            }
        )
        is_request_valid = validation_result['validation_output'].plan_is_valid
        print('Validation object:', validation_result['validation_output'])
        if is_request_valid == 'no':
            raise ValueError('UNREASONABLE_REQUEST')
        
        validation_test = validation_result["agent_suggestion"]
        output = json.loads(validation_test.strip())
        output = enrich_params(output)
            
        t2 = time.time()
        self.logger.info("Time to validate request: {}".format(round(t2 - t1, 2)))

        return output
