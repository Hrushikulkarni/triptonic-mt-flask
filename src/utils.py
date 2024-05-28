import os
import math
from dotenv import load_dotenv
from pathlib import Path
import datetime
import numpy as np
import re
from unidecode import unidecode

def clean_timing(text):
  if text.lower() == 'open 24 hours':
    return '12:00 AM - 11:59 PM'
  # Transliterate text to ASCII
  text = unidecode(text)
  
  # Replace non-ASCII dashes with a regular dash
  text = re.sub(r'[\u2013\u2014\u2015]', '-', text)
  
  # Add space between time and AM/PM if missing
  text = re.sub(r'(\d)([APM])', r'\1 \2', text)

  # Ensure there is a colon between hours and minutes
  text = re.sub(r'(\d{1,2})(\d{2})', r'\1:\2', text)

  # Replace special characters and fix spacing issues
  text = text.replace(' ', ' ')  # Replace non-breaking spaces (U+202F) with regular space
  text = text.replace(' ', ' ')  # Replace thin spaces (U+2009) with regular space
  
  # Normalize multiple spaces to a single space
  text = re.sub(r'\s+', ' ', text)

  # Add AM to the first time segment if missing
  if '-' in text:
    before_dash, after_dash = text.split('-', 1)
    if not re.search(r'[APM]', before_dash):
      before_dash += 'AM'
    text = before_dash + ' -' + after_dash
  
  return text.strip()

def calculate_minmax_score(places):
  ratings = np.array([place['rating'] for place in places])
  user_ratings_totals = np.array([place['user_ratings_total'] for place in places])
  rmin, rmax = ratings.min(), ratings.max()
  print(rmin, rmax)
  umin, umax = user_ratings_totals.min(), user_ratings_totals.max()
  print(umin, umax)

  if rmin == rmax:
    normalized_ratings = np.full_like(ratings, 0.5)
  else:
    normalized_ratings = (ratings - rmin) / (rmax - rmin)

  if umin == umax:
    normalized_user_ratings_totals = np.full_like(user_ratings_totals, 0.5)
  else:
    normalized_user_ratings_totals = (user_ratings_totals - umin) / (umax - umin)

  combined_scores = normalized_ratings * 0.5 + normalized_user_ratings_totals * 0.5

  for i, place in enumerate(places):
    place['score'] = combined_scores[i] if combined_scores[i] > 0.05 else 0.4
  return places

def get_top_n_places(n, places):
  if not places:
    return []

  places = calculate_minmax_score(places)
  sorted_places = sorted(places, key=lambda x: x['score'], reverse=True)

  return sorted_places[:n]

def get_timings_for_today(timings):
  current_day_name = datetime.datetime.now().strftime("%A")
  for timing in timings:
    if current_day_name.lower() in timing.lower():
      return clean_timing(''.join(timing.split(':')[1:]).split(',')[0])
  return '10:00 AM - 06:00 PM'

def load_secrets():
  load_dotenv()
  env_path = Path("..") / ".env"
  load_dotenv(dotenv_path=env_path)

  google_gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")
  google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
  mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
  website_domain = os.getenv("WEBSITE_DOMAIN")

  return {
    "GOOGLE_GEMINI_API_KEY": google_gemini_key,
    "GOOGLE_MAPS_API_KEY": google_maps_key,
    "MONGO_CONNECTION_STRING": mongo_connection_string,
    "WEBSITE_DOMAIN": website_domain
  }

def clean_google_maps_data(place_type, places):
  data = []
  for place in places:
    data.append({
      'id': place.get('place_id'),
      'type': place_type,
      'name': place.get('name', ''),
      'website': place.get('website', ''),
      'description': place.get('editorial_summary', {}).get('overview', ''),
      'latitude': place.get('geometry', {}).get('location', {}).get('lat', 0),
      'longitude': place.get('geometry', {}).get('location', {}).get('lng', 0),
      'latitudeDelta': 1,
      'longitudeDelta': 1,
      'business_status': place.get('business_status', 'OPERATIONAL'),
      'serves': prepare_servings(place),
      'rating': place.get('rating', 3),
      'total_reviews': place.get('user_ratings_total', 1),
      'price_range': place.get('price_level', 2),
      'todays_working_hours': get_timings_for_today(place.get('current_opening_hours', {}).get('weekday_text', [])),
      'notes': 'Notes...',
      'score': place.get('score', 0.5)
    })
  return data


def haversine(lat1, lon1, lat2, lon2):
  R = 6371.0  # Radius of the Earth in kilometers
  lat1_rad = math.radians(lat1)
  lon1_rad = math.radians(lon1)
  lat2_rad = math.radians(lat2)
  lon2_rad = math.radians(lon2)

  dlat = lat2_rad - lat1_rad
  dlon = lon2_rad - lon1_rad

  a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

  distance = R * c
  return distance

def calculate_centroid(points):
  total_lat = sum(point['latitude'] for point in points)
  total_lon = sum(point['longitude'] for point in points)
  
  centroid_lat = total_lat / len(points)
  centroid_lon = total_lon / len(points)
  
  return (centroid_lat, centroid_lon)

def filter_points_within_radius(points, centroid, radius_km):
  filtered_points = []
  for point in points:
    distance = haversine(centroid[0], centroid[1], point['latitude'], point['longitude'])
    if distance <= radius_km:
      filtered_points.append(point)
  return filtered_points

def prepare_servings(place):
  servings = []
  if place.get('serves_breakfast'):
    servings.append('breakfast')
  elif place.get('serves_brunch'):
    servings.append('brunch')
  elif place.get('serves_lunch'):
    servings.append('lunch')
  elif place.get('serves_dinner'):
    servings.append('dinner')
  return servings

def filter_farther_places_and_flatten(distance, places):
  centroid = calculate_centroid(places['transit'])
  non_transit_places = filter_points_within_radius(places['restaurant'], centroid, distance) + filter_points_within_radius(places['tourist'], centroid, distance)

  return places['transit'] + non_transit_places

def parse_working_hours(hours_str):
  start_str, end_str = hours_str.split('-')
  start_time = datetime.datetime.strptime(start_str.strip(), "%I:%M %p").time()
  end_time = datetime.datetime.strptime(end_str.strip(), "%I:%M %p").time()
  
  return start_time, end_time

def parse_24_hour_time(time_str):
  start_str, end_str = time_str.split('-')
  start_time = datetime.datetime.strptime(start_str.strip(), "%H:%M").time()
  end_time = datetime.datetime.strptime(end_str.strip(), "%H:%M").time()
  
  return start_time, end_time

def filter_places_by_time(places, time_str):
  filter_start, filter_end = parse_24_hour_time(time_str)
  filtered_places = []
  for place in places:
    try:
      place_start, place_end = parse_working_hours(place.get('todays_working_hours', '10:00 AM - 06:00 PM'))
    except Exception as e:
      print('Error', e, place.get('todays_working_hours', '10:00 AM - 06:00 PM'), place.get('id'))
      continue
    if filter_start <= place_end and place_start <= filter_end:
      filtered_places.append(place)
  return filtered_places

def within_budget(budget, price_range):
  if budget == 'low':
    return price_range <= 1
  elif budget == 'medium':
    return price_range == 2
  return price_range > 2 and price_range < 5

def duration_places_count(duration):
  if duration <= 1:
    return 4
  elif duration <= 2:
    return 8
  elif duration <= 3:
    return 12
  return 20

def stats_printer(places):
  print('Total restaurant places:', len([p for p in places if p['type'] == 'restaurant']))
  print('Total tourist places:', len([p for p in places if p['type'] == 'tourist']))
  print('Total transit places:', len([p for p in places if p['type'] == 'transit']))
