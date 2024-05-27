import os
from dotenv import load_dotenv
from pathlib import Path
import datetime
import numpy as np

def get_top_10_places(places):
  if not places:
    return []

  ratings = np.array([place['rating'] for place in places])
  user_ratings_totals = np.array([place['user_ratings_total'] for place in places])

  normalized_ratings = (ratings - ratings.min()) / (ratings.max() - ratings.min())
  normalized_user_ratings_totals = (user_ratings_totals - user_ratings_totals.min()) / (user_ratings_totals.max() - user_ratings_totals.min())

  combined_scores = normalized_ratings * 0.5 + normalized_user_ratings_totals * 0.5

  for i, place in enumerate(places):
    place['combined_score'] = combined_scores[i]

  sorted_places = sorted(places, key=lambda x: x['combined_score'], reverse=True)

  return sorted_places[:10]

def get_timings_for_today(timings):
  current_day_name = datetime.datetime.now().strftime("%A")
  for timing in timings:
    if current_day_name.lower() in timing.lower():
      return timing

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

def populate_price_range(price_level):
  if price_level <= 1:
    return 'low'
  if price_level <= 2:
    return 'medium'
  return 'high'

def clean_google_maps_data(places):
  def helper(place_type):
    data = []
    for place in places.get(place_type, []):
      data.append({
        'type': place_type,
        'business_status': place.get('business_status', 'OPERATIONAL'),
        'name': place.get('name', ''),
        'rating': place.get('rating', 3),
        'total_reviews': place.get('user_ratings_total', 1),
        'price_range': populate_price_range(place.get('price_level', 2)),
        'todays_working_hours': get_timings_for_today(place.get('current_opening_hours', {}).get('weekday_text', [])) 
      })
    return data
  