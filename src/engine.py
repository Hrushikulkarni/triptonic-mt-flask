import datetime
import math

class Engine(object):
    @staticmethod
    def ordering(data, user_location):
        if not user_location:
            return data

        user_lat, user_lng = user_location
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371.0
            lat1 = math.radians(lat1)
            lon1 = math.radians(lon1)
            lat2 = math.radians(lat2)
            lon2 = math.radians(lon2)
            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c

            return distance

        def calculate_place_distance(place):
            place_lat = place['geometry']['location']['lat']
            place_lng = place['geometry']['location']['lng']
            return calculate_distance(user_lat, user_lng, place_lat, place_lng)

        restaurants = data.get('restaurant', {}).get('results', [])
        restaurants.sort(key=lambda r: calculate_place_distance(r))

        tourist_places = data.get('tourist', {}).get('results', [])
        tourist_places.sort(key=lambda t: calculate_place_distance(t))

        # Combine the ordered restaurants and tourist places
        ordered_data = {
            'restaurant': {'results': restaurants},
            'tourist': {'results': tourist_places}
        }

        return ordered_data


    @staticmethod
    def filtering(data, cuisine=None, budget=None, timings=None):
        filtered = []

        def parse_timings(timings):
            start_time, end_time = timings.split('-')
            start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_time, "%H:%M").time()
            return start_time, end_time

        # Helper function to check if current time falls within the given range
        def is_within_time_range(opening_hours, start_time, end_time):
            if not opening_hours:
                return False
            periods = opening_hours.get('periods', [])
            for period in periods:
                if 'open' in period and 'close' in period:
                    open_time = datetime.datetime.strptime(period['open']['time'], "%H%M").time()
                    close_time = datetime.datetime.strptime(period['close']['time'], "%H%M").time()
                    if start_time <= open_time <= end_time or start_time <= close_time <= end_time:
                        return True
            return False

    
        restaurants = data.get('restaurant', {}).get('results', [])
        if cuisine:
            restaurants = [r for r in restaurants if cuisine.lower() in [type_.lower() for type_ in r.get('types', [])]]
        if budget:
            restaurants = [r for r in restaurants if r.get('price_level') is not None and int(r.get('price_level')) <= budget]

        tourist_places = data.get('tourist', {}).get('results', [])
        if timings:
            start_time, end_time = parse_timings(timings)
            tourist_places = [t for t in tourist_places if is_within_time_range(t.get('opening_hours', {}), start_time, end_time)]

        filtered.extend(restaurants)
        filtered.extend(tourist_places)

        return filtered

    
    @staticmethod
    def covertFlat(data):
        flatData = []

        for row in data:
            flatRow = {}
            flatRow['latitude'] = row['geometry']['location']['lat']
            flatRow['longitude'] = row['geometry']['location']['lng']
            flatRow['latitudeDelta'] = 1
            flatRow['longitudeDelta'] = 1
            flatRow['icon'] = row['icon']
            flatRow['name'] = row['name']
            flatRow['rating'] = row['rating']
            flatRow['photos'] = row['photos'][0]
            flatData.append(flatRow)
        
        return flatData