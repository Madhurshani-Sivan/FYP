
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.exc import GeocoderServiceError

def order_universities(student_preferences, universities_collection, weight):
    # Update proximity attribute based on student preferences
    update_proximity_attribute(student_preferences, universities_collection)

    # Get importance ratings from student preferences
    proximity_importance = int(student_preferences.get('proximity_importance', 1))
    cost_importance = int(student_preferences.get('cost_importance', 1))

    # Initialize an empty list to store universities with their scores
    university_scores = []

    # Calculate scores for each university based on proximity, cost, and entertainment
    for doc in universities_collection.find():
        university_code = doc['code']
        proximity = doc.get('proximity', 1)
        cost = doc['cost']
        university_name = doc['name']

        # Calculate the score for each university based on preferences
        proximity_score = proximity * (5-proximity_importance )
        cost_score = cost * (5-cost_importance)

        # Calculate the total score for the university
        total_score = proximity_score + cost_score + weight

        # Append the university code, name, and total score to the university_scores list
        university_scores.append((university_code, university_name, total_score))

    # Sort the universities based on the total score in descending order
    university_scores.sort(key=lambda x: x[2], reverse=True)

    # Extract the ordered list of university codes
    ordered_universities = [name for name, _, _ in university_scores]

    return ordered_universities

def update_proximity_attribute(student_preferences, universities_collection):
    home_city = student_preferences.get('home_city')

    for doc in universities_collection.find():
        university_city = doc['city']

        proximity = calculate_proximity(home_city, university_city)

        # Update the document in the collection with the new proximity attribute
        universities_collection.update_one({"city": university_city}, {"$set": {"proximity": proximity}})
        
def calculate_proximity(home_city, university_city):
    # Geocode the cities to obtain coordinates
    geolocator = Nominatim(user_agent="your_app_name")

    try:
        location_home = geolocator.geocode(home_city)
        location_university = geolocator.geocode(university_city)

        if location_home is not None and location_university is not None:
            # Get the latitude and longitude for each city
            coords_home = (location_home.latitude, location_home.longitude)
            coords_university = (location_university.latitude, location_university.longitude)

            # Calculate the distance between the coordinates using geodesic
            distance = geodesic(coords_home, coords_university).kilometers

            # Assign a proximity rating between 1 and 5 based on the distance
            if distance <= 50:
                proximity_rating = 1
            elif distance <= 100:
                proximity_rating = 2
            elif distance <= 150:
                proximity_rating = 3
            elif distance <= 200:
                proximity_rating = 4
            else:
                proximity_rating = 5

            return proximity_rating
    except (GeocoderTimedOut, GeocoderServiceError):
        # Handle timeout or service error and retry geocoding
        return calculate_proximity(home_city, university_city)

    return None
