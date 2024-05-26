import sys
import os

# Add the parent directory of 'src' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import load_secrets
from src.llm.agent import Agent

if __name__ == '__main__':
    secrets = load_secrets()
    travel_agent = Agent(google_gemini_key=secrets['GOOGLE_GEMINI_API_KEY'], debug=True)

    query = """
            Plan a family trip to San Diego from Irvine for 2 days covering historical places with Italian cuisine. For a family of five with a tight budget and daily travel from 6 AM to 5 PM.
            """
    output = travel_agent.validate_travel(query)
    print(output)

    filtered_output = travel_agent.validate_filtering(output)
    print(filtered_output)
    
