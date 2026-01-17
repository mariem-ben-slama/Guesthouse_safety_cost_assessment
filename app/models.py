from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy (the database tool)
db = SQLAlchemy()

class Owner(db.Model):
    """
    Represents a guesthouse owner account.
    This is like a user account in any application.
    """
    __tablename__ = 'owners'
    
    # Primary key - unique ID for each owner
    id = db.Column(db.Integer, primary_key=True)
    
    # Owner information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Password is stored as a hash (encrypted), never as plain text!
    password_hash = db.Column(db.String(255), nullable=False)
    
    # When the account was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: one owner can have multiple guesthouses
    guesthouses = db.relationship('Guesthouse', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash the password before storing it.
        This is a security best practice - we never store plain passwords!
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        Returns True if correct, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        Convert owner object to a dictionary (for JSON responses).
        Note: We never include the password hash in responses!
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Guesthouse(db.Model):
    """
    Represents a guesthouse with all its safety-related information.
    This stores everything we need to calculate safety scores.
    """
    __tablename__ = 'guesthouses'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key - links to the owner
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    
    # Basic information
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    
    # Location coordinates (for finding nearby hospitals and weather)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Building information
    construction_year = db.Column(db.Integer, nullable=False)
    number_of_floors = db.Column(db.Integer, nullable=False)
    number_of_rooms = db.Column(db.Integer, nullable=False)
    
    # Safety equipment (these determine the baseline safety score)
    fire_extinguishers = db.Column(db.Integer, default=0)
    smoke_detectors = db.Column(db.Integer, default=0)
    emergency_exits = db.Column(db.Integer, default=0)
    has_first_aid_kit = db.Column(db.Boolean, default=False)
    
    # Stair safety
    has_stair_handrails = db.Column(db.Boolean, default=False)
    stairs_slip_resistant = db.Column(db.Boolean, default=False)
    
    # Optional: Building type affects installation cost complexity
    # Values: 'modern', 'traditional', 'renovated'
    # Default to 'traditional' if not specified (most common in Tunisia)
    building_type = db.Column(db.String(20), default='traditional')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        Convert guesthouse object to a dictionary (for JSON responses).
        """
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'construction_year': self.construction_year,
            'number_of_floors': self.number_of_floors,
            'number_of_rooms': self.number_of_rooms,
            'fire_extinguishers': self.fire_extinguishers,
            'smoke_detectors': self.smoke_detectors,
            'emergency_exits': self.emergency_exits,
            'has_first_aid_kit': self.has_first_aid_kit,
            'has_stair_handrails': self.has_stair_handrails,
            'stairs_slip_resistant': self.stairs_slip_resistant,
            'building_type': self.building_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }