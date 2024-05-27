from .utils import *
from .llm.agent import Agent

secrets = load_secrets()

class Engine(object):
    def __init__(self) -> None:
        self.llm_api_key = secrets['GOOGLE_GEMINI_API_KEY']
        self.agent = Agent(google_gemini_key=self.llm_api_key, debug=True)

    def order(self, places, params):
        query = f'''
            {places}
            PARAMETER {params}
        '''
        backup = sorted(places, key=lambda x: x['score'], reverse=True)
        try:
            llm_output = self.agent.generate_trip(query)
            if len(llm_output) <= 3:
                print('BACKUP RECOMMENDATION')
                return backup[:duration_places_count(params['duration'])]
            return llm_output
        except Exception as e:
            print('ERROR in recommenation engine:', e)
            return backup

    def filter(self, places, params):
        print('Before any filter:', len(places))
        filtered = filter_farther_places_and_flatten(params.get('distance'), places)
        print('Filter based on distance:', len(filtered))

        filtered = filter_places_by_time(filtered, params.get('timings', '07:00-20:00'))
        print('Filter based on timings:', len(filtered))

        # filtered = [place for place in filtered if within_budget(params.get('budget', 'medium'), place['price_range'])]
        # print('Filter based on budget:', len(filtered))

        filtered = [place for place in filtered if place.get('score') is None or place.get('score') >= 0.3]
        print('Filter based on score:', len(filtered))

        filtered = [place for place in filtered if place.get('business_status').lower() == 'operational']
        print('Filter based on business status:', len(filtered))

        return filtered