import json
from langchain.chains import LLMChain, SequentialChain
from langchain_google_genai import GoogleGenerativeAI
from src.llm.templates import (
    ValidationTemplate,
    ExtractParametersTemplate
)
from src.constants import MODEL_NAME, TEMPERATURE
import logging
import time

logging.basicConfig(level=logging.INFO)

class Agent(object):
    def __init__(
        self,
        google_gemini_key,
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        debug=True,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._openai_key = google_gemini_key

        self.chat_model = GoogleGenerativeAI(model=model, temperature=temperature, google_api_key=self._openai_key)
        self.validation_prompt = ValidationTemplate()
        self.extract_parameters_prompt = ExtractParametersTemplate()
        self.validation_chain = self._set_up_validation_chain(debug)

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
            output_variables=["validation_output", "agent_suggestion"],
            verbose=debug,
        )

        return overall_chain

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

        validation_test = validation_result["agent_suggestion"]
        output = json.loads(validation_test.strip())
        t2 = time.time()
        self.logger.info("Time to validate request: {}".format(round(t2 - t1, 2)))

        return output
