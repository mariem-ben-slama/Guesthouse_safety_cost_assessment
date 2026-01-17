from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, Owner

# Create a Blueprint for authentication routes
# Think of this as a mini-app that handles login/signup
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new guesthouse owner.
    
    Expected JSON body:
    {
        "name": "Owner Name",
        "email": "owner@example.com",
        "password": "securepassword"
    }
    
    Returns:
        201: Account created successfully
        400: Missing required fields or email already exists
    """
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    # Check all required fields are present
    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400
    
    # Check if email already exists
    if Owner.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    # Create new owner
    owner = Owner(name=name, email=email)
    owner.set_password(password)  # This hashes the password
    
    try:
        db.session.add(owner)
        db.session.commit()
        
        return jsonify({
            'message': 'Account created successfully',
            'owner': owner.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create account'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate an owner and return a JWT token.
    
    Expected JSON body:
    {
        "email": "owner@example.com",
        "password": "securepassword"
    }
    
    Returns:
        200: Login successful with JWT token
        400: Missing credentials
        401: Invalid credentials
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find owner by email
    owner = Owner.query.filter_by(email=email).first()
    
    # Check if owner exists and password is correct
    if not owner or not owner.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create JWT token (this is what the owner will use for authenticated requests)
    access_token = create_access_token(identity=str(owner.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'owner': owner.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_owner():
    """
    Get information about the currently authenticated owner.
    Requires JWT token in Authorization header.
    
    Returns:
        200: Owner information
        404: Owner not found
    """
    # Get owner ID from JWT token
    current_owner_id = int(get_jwt_identity())
    
    owner = Owner.query.get(current_owner_id)
    
    if not owner:
        return jsonify({'error': 'Owner not found'}), 404
    
    return jsonify({
        'owner': owner.to_dict()
    }), 200