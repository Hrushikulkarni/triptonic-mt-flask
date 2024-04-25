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
            Plan a family trip to San Diego covering historical places with Indian cuisine. For a family of five with a tight budget.
            """
    output = travel_agent.validate_travel(query)
    print(output)
