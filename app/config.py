import os
from datetime import timedelta

class Config:
    """
    Configuration class for the Flask application.
    Loads settings from environment variables with sensible defaults.
    """
    
    # Database configuration
    # SQLite database will be created in the 'instance' folder
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI', 
        'sqlite:///guesthouse.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    # This secret key is used to sign JWT tokens - keep it secret!
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT tokens expire after 24 hours for security
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # API Information
    API_TITLE = os.getenv('API_TITLE', 'Guesthouse Safety API')
    API_VERSION = os.getenv('API_VERSION', '1.0')
    
    # External API endpoints
    # Open-Meteo: Free weather API, no key required
    WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast'
    
    # Overpass API: OpenStreetMap data for nearby facilities, no key required
    OVERPASS_API_URL = 'https://overpass-api.de/api/interpreter'
    
    # Safety cost estimates (in Tunisian Dinars - TND)
    # Based on 2024-2026 Tunisian market research
    
    # EQUIPMENT COSTS (material only)
    EQUIPMENT_COSTS = {
        'fire_extinguisher': 100,      # 6kg ABC powder extinguisher
        'smoke_detector': 50,           # Battery-powered detector
        'emergency_exit_sign': 65,      # LED illuminated sign
        'first_aid_kit': 130,           # Complete professional kit
        'stair_handrail': 150,          # Material per meter (avg 3-4m per floor)
        'slip_resistant_coating': 250   # Anti-slip material per staircase
    }
    
    # INSTALLATION & LABOR COSTS
    # These are added on top of equipment costs
    INSTALLATION_COSTS = {
        'fire_extinguisher': 20,        # Wall mounting, positioning
        'smoke_detector': 15,           # Ceiling installation, wiring
        'emergency_exit_sign': 35,      # Electrical work, positioning
        'first_aid_kit': 0,             # No installation needed
        'stair_handrail': 80,           # Per meter installation (welding, securing)
        'slip_resistant_coating': 150   # Labor for surface preparation & application
    }
    
    # COMPLIANCE & INSPECTION COSTS
    # Required for legal compliance and certification
    COMPLIANCE_COSTS = {
        'fire_safety_inspection': 200,   # Initial fire safety inspection
        'safety_certification': 150,     # Official safety certificate
        'annual_fire_inspection': 100    # Recurring annual inspection
    }
    
    # MAINTENANCE COSTS (annual estimates)
    MAINTENANCE_COSTS = {
        'fire_extinguisher': 15,         # Annual service/refill per unit
        'smoke_detector': 8,             # Battery replacement, testing
        'emergency_exit_sign': 10,       # Bulb replacement, cleaning
        'first_aid_kit': 50,             # Restocking supplies
        'stair_handrail': 20,            # Inspection, minor repairs per unit
        'slip_resistant_coating': 0      # One-time application, 5+ year lifespan
    }
    
    # OPTIONAL SAFETY IMPROVEMENTS
    # Recommendations for enhanced safety (not mandatory)
    OPTIONAL_IMPROVEMENTS = {
        'fire_blanket': 80,              # Kitchen fire safety
        'emergency_lighting': 120,       # Battery backup lighting per floor
        'carbon_monoxide_detector': 90,  # Per detector (recommended for kitchens)
        'security_camera': 250,          # Per camera (entrance/common areas)
        'fire_alarm_system': 800,        # Centralized alarm system (for larger properties)
        'emergency_evacuation_plan': 150 # Professional signage and floor plans
    }
    
    # BUILDING TYPE MULTIPLIERS (affects installation complexity)
    # If owner doesn't specify, assume "traditional" (multiplier = 1.0)
    BUILDING_TYPE_MULTIPLIERS = {
        'modern': 0.9,      # Easier installation (standard construction)
        'traditional': 1.0,  # Standard difficulty (medina-style, stone buildings)
        'renovated': 1.1     # Moderate difficulty (mixed old/new structure)
    }
    
    # Safety thresholds
    # These numbers determine what's considered safe
    SAFETY_THRESHOLDS = {
        'min_fire_extinguishers_per_floor': 1,
        'min_smoke_detectors_per_floor': 2,
        'min_emergency_exits': 2,
        'old_building_year': 1990,  # Buildings older than this get flagged
        'nearby_hospital_radius_km': 5,  # Search radius for hospitals
        'nearby_pharmacy_radius_km': 2   # Search radius for pharmacies
    }