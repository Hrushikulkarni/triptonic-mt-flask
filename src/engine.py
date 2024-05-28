from .utils import *
from .llm.agent import Agent
from datetime import datetime, timedelta

secrets = load_secrets()

class Engine(object):
    def __init__(self) -> None:
        self.llm_api_key = secrets['GOOGLE_GEMINI_API_KEY']
        self.agent = Agent(google_gemini_key=self.llm_api_key, debug=True)

    def populate_day_time(self, llm_output, params):
    
        duration = params['duration']

        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("20:00", "%H:%M")
    
        total_time_minutes = int((end_time - start_time).total_seconds() / 60)
        items = [item for item in llm_output if item != 'prompt']
        total_items = len(items)
        items_per_day = total_items // duration
        extra_items = total_items % duration

        current_day = 1
        current_time = start_time

        for i, item in enumerate(items):
            if 'day' not in item:
                item['day'] = current_day
            if 'time' not in item:
                item['time'] = current_time.strftime("%H:%M")
        
            increment_minutes = total_time_minutes // items_per_day
            current_time += timedelta(minutes=increment_minutes)

        
            if current_time >= end_time:
                current_day += 1
                current_time = start_time
                if current_day > duration:
                    current_day = duration  # Prevent going beyond the last day
        
        
            if extra_items > 0:
                if i < extra_items:
                    item['day'] = current_day
                    item['time'] = current_time.strftime("%H:%M")
                    current_time += timedelta(minutes=increment_minutes)
                    if current_time >= end_time:
                        current_day += 1
                        current_time = start_time
                        if current_day > duration:
                            current_day = duration  # Prevent going beyond the last day

        return llm_output

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
                modified_backup = backup[:duration_places_count(params['duration'])]
                return self.populate_day_time(modified_backup, params)
            return self.populate_day_time(llm_output, params)
        except Exception as e:
            print('ERROR in recommenation engine:', e)
            return self.populate_day_time(backup, params)

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