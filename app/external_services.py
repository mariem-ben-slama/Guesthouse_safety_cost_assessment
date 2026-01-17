import requests
from flask import current_app

class WeatherService:
    """
    Fetches current weather data from Open-Meteo API.
    Open-Meteo is free and doesn't require an API key.
    """
    
    @staticmethod
    def get_current_weather(latitude, longitude):
        """
        Get current weather conditions for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            dict with weather data or None if request fails
        """
        try:
            url = current_app.config['WEATHER_API_URL']
            
            # Parameters for the weather API
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,precipitation,rain,wind_speed_10m',
                'timezone': 'auto'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current', {})
            
            # Extract relevant weather information
            return {
                'temperature': current.get('temperature_2m', 0),
                'precipitation': current.get('precipitation', 0),
                'rain': current.get('rain', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
                'time': current.get('time', '')
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return None
    
    @staticmethod
    def analyze_weather_risks(weather_data):
        """
        Analyze weather data and identify potential risks.
        
        Args:
            weather_data: Dictionary containing weather information
            
        Returns:
            dict with risk level and recommendations
        """
        if not weather_data:
            return {
                'risk_level': 'unknown',
                'risk_score': 0,
                'recommendations': ['Weather data unavailable']
            }
        
        risk_score = 0
        recommendations = []
        
        # Check temperature risks
        temp = weather_data.get('temperature', 20)
        if temp > 35:
            risk_score += 15
            recommendations.append('High temperature: Ensure adequate ventilation and provide water for guests')
        elif temp < 5:
            risk_score += 10
            recommendations.append('Low temperature: Check heating systems and warn guests about cold conditions')
        
        # Check precipitation/rain risks
        rain = weather_data.get('rain', 0)
        precipitation = weather_data.get('precipitation', 0)
        if rain > 0 or precipitation > 0:
            risk_score += 20
            recommendations.append('Rainy conditions: Place warning signs on stairs, check for water leaks, ensure walkways are dry')
        
        # Check wind risks
        wind_speed = weather_data.get('wind_speed', 0)
        if wind_speed > 30:
            risk_score += 25
            recommendations.append('Strong winds: Secure outdoor furniture, close terrace/rooftop areas, warn guests')
        elif wind_speed > 20:
            risk_score += 10
            recommendations.append('Moderate winds: Check outdoor areas and secure loose items')
        
        # Determine risk level
        if risk_score >= 40:
            risk_level = 'high'
        elif risk_score >= 20:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'recommendations': recommendations if recommendations else ['No weather-related risks detected']
        }


class EmergencyFacilitiesService:
    """
    Finds nearby hospitals and pharmacies using OpenStreetMap Overpass API.
    Overpass is free and doesn't require an API key.
    """
    
    @staticmethod
    def find_nearby_facilities(latitude, longitude, radius_km=5):
        """
        Find nearby hospitals and pharmacies within a given radius.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_km: Search radius in kilometers
            
        Returns:
            dict with counts of nearby facilities
        """
        try:
            url = current_app.config['OVERPASS_API_URL']
            
            # Convert km to meters for the Overpass API
            radius_m = radius_km * 1000
            
            # Overpass QL query to find hospitals and pharmacies
            # This query searches for both amenities within the radius
            query = f"""
            [out:json];
            (
              node["amenity"="hospital"](around:{radius_m},{latitude},{longitude});
              way["amenity"="hospital"](around:{radius_m},{latitude},{longitude});
              node["amenity"="pharmacy"](around:{radius_m},{latitude},{longitude});
              way["amenity"="pharmacy"](around:{radius_m},{latitude},{longitude});
            );
            out count;
            """
            
            response = requests.post(url, data={'data': query}, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            elements = data.get('elements', [])
            
            # Count hospitals and pharmacies
            hospitals = sum(1 for elem in elements if elem.get('tags', {}).get('amenity') == 'hospital')
            pharmacies = sum(1 for elem in elements if elem.get('tags', {}).get('amenity') == 'pharmacy')
            
            return {
                'hospitals': hospitals,
                'pharmacies': pharmacies,
                'radius_km': radius_km
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Overpass API error: {e}")
            return {
                'hospitals': 0,
                'pharmacies': 0,
                'radius_km': radius_km,
                'error': 'Unable to fetch facility data'
            }
    
    @staticmethod
    def analyze_facility_access(facilities_data):
        """
        Analyze proximity to emergency facilities and calculate risk impact.
        
        Args:
            facilities_data: Dictionary with hospital and pharmacy counts
            
        Returns:
            dict with risk adjustment and recommendations
        """
        hospitals = facilities_data.get('hospitals', 0)
        pharmacies = facilities_data.get('pharmacies', 0)
        
        risk_adjustment = 0
        recommendations = []
        
        # Hospital proximity analysis
        if hospitals == 0:
            risk_adjustment += 20
            recommendations.append('No hospitals nearby: Consider providing emergency contact numbers and basic medical training for staff')
        elif hospitals == 1:
            risk_adjustment += 10
            recommendations.append('Limited hospital access: Keep emergency contact information readily available')
        else:
            recommendations.append('Good hospital access in the area')
        
        # Pharmacy proximity analysis
        if pharmacies == 0:
            risk_adjustment += 10
            recommendations.append('No pharmacies nearby: Maintain a well-stocked first aid kit with common medications')
        elif pharmacies < 2:
            risk_adjustment += 5
            recommendations.append('Limited pharmacy access: Keep basic medical supplies on hand')
        else:
            recommendations.append('Good pharmacy access in the area')
        
        return {
            'risk_adjustment': risk_adjustment,
            'recommendations': recommendations
        }