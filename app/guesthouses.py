from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Guesthouse, Owner
from app.safety import SafetyAssessment
from app.external_services import WeatherService, EmergencyFacilitiesService

# Create a Blueprint for guesthouse routes
guesthouses_bp = Blueprint('guesthouses', __name__, url_prefix='/api/guesthouses')


@guesthouses_bp.route('', methods=['POST'])
@jwt_required()
def create_guesthouse():
    """
    Create a new guesthouse for the authenticated owner.
    
    Expected JSON body:
    {
        "name": "My Guesthouse",
        "address": "123 Street, Tunis",
        "latitude": 36.8065,
        "longitude": 10.1815,
        "construction_year": 2010,
        "number_of_floors": 2,
        "number_of_rooms": 5,
        "fire_extinguishers": 2,
        "smoke_detectors": 4,
        "emergency_exits": 2,
        "has_first_aid_kit": true,
        "has_stair_handrails": true,
        "stairs_slip_resistant": false
    }
    
    Returns:
        201: Guesthouse created successfully
        400: Missing or invalid fields
    """
    current_owner_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields
    required_fields = ['name', 'address', 'latitude', 'longitude', 'construction_year', 
                      'number_of_floors', 'number_of_rooms']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Create new guesthouse
        # Optional building type (affects installation cost complexity)
        building_type = data.get('building_type', 'traditional')
        if building_type not in ['modern', 'traditional', 'renovated']:
            building_type = 'traditional'
        
        guesthouse = Guesthouse(
            owner_id=current_owner_id,
            name=data['name'],
            address=data['address'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            construction_year=int(data['construction_year']),
            number_of_floors=int(data['number_of_floors']),
            number_of_rooms=int(data['number_of_rooms']),
            fire_extinguishers=int(data.get('fire_extinguishers', 0)),
            smoke_detectors=int(data.get('smoke_detectors', 0)),
            emergency_exits=int(data.get('emergency_exits', 0)),
            has_first_aid_kit=bool(data.get('has_first_aid_kit', False)),
            has_stair_handrails=bool(data.get('has_stair_handrails', False)),
            stairs_slip_resistant=bool(data.get('stairs_slip_resistant', False)),
            building_type=building_type
        )
        
        db.session.add(guesthouse)
        db.session.commit()
        
        return jsonify({
            'message': 'Guesthouse created successfully',
            'guesthouse': guesthouse.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid field value: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create guesthouse'}), 500


@guesthouses_bp.route('', methods=['GET'])
@jwt_required()
def list_guesthouses():
    """
    Get all guesthouses owned by the authenticated owner.
    
    Returns:
        200: List of guesthouses
    """
    current_owner_id = get_jwt_identity()
    
    guesthouses = Guesthouse.query.filter_by(owner_id=current_owner_id).all()
    
    return jsonify({
        'guesthouses': [g.to_dict() for g in guesthouses],
        'count': len(guesthouses)
    }), 200


@guesthouses_bp.route('/<int:guesthouse_id>', methods=['GET'])
@jwt_required()
def get_guesthouse(guesthouse_id):
    """
    Get details of a specific guesthouse.
    Owner can only access their own guesthouses.
    
    Returns:
        200: Guesthouse details
        403: Not authorized
        404: Guesthouse not found
    """
    current_owner_id = get_jwt_identity()
    
    guesthouse = Guesthouse.query.get(guesthouse_id)
    
    if not guesthouse:
        return jsonify({'error': 'Guesthouse not found'}), 404
    
    # Check ownership
    if int(guesthouse.owner_id) != int(current_owner_id):
        return jsonify({'error': 'Not authorized to access this guesthouse'}), 403
    
    return jsonify({
        'guesthouse': guesthouse.to_dict()
    }), 200


@guesthouses_bp.route('/<int:guesthouse_id>', methods=['PUT'])
@jwt_required()
def update_guesthouse(guesthouse_id):
    """
    Update guesthouse information.
    Owner can only update their own guesthouses.
    
    Returns:
        200: Guesthouse updated successfully
        403: Not authorized
        404: Guesthouse not found
    """
    current_owner_id = get_jwt_identity()
    
    guesthouse = Guesthouse.query.get(guesthouse_id)
    
    if not guesthouse:
        return jsonify({'error': 'Guesthouse not found'}), 404
    
    if int(guesthouse.owner_id) != int(current_owner_id):
        return jsonify({'error': 'Not authorized to update this guesthouse'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update fields if provided
        updatable_fields = ['name', 'address', 'latitude', 'longitude', 'construction_year',
                           'number_of_floors', 'number_of_rooms', 'fire_extinguishers',
                           'smoke_detectors', 'emergency_exits', 'has_first_aid_kit',
                           'has_stair_handrails', 'stairs_slip_resistant']
        
        for field in updatable_fields:
            if field in data:
                setattr(guesthouse, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Guesthouse updated successfully',
            'guesthouse': guesthouse.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update guesthouse'}), 500


@guesthouses_bp.route('/<int:guesthouse_id>', methods=['DELETE'])
@jwt_required()
def delete_guesthouse(guesthouse_id):
    """
    Delete a guesthouse.
    Owner can only delete their own guesthouses.
    
    Returns:
        200: Guesthouse deleted successfully
        403: Not authorized
        404: Guesthouse not found
    """
    current_owner_id = get_jwt_identity()
    
    guesthouse = Guesthouse.query.get(guesthouse_id)
    
    if not guesthouse:
        return jsonify({'error': 'Guesthouse not found'}), 404
    
    if int(guesthouse.owner_id) != int(current_owner_id):
        return jsonify({'error': 'Not authorized to delete this guesthouse'}), 403
    
    try:
        db.session.delete(guesthouse)
        db.session.commit()
        
        return jsonify({
            'message': 'Guesthouse deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete guesthouse'}), 500


@guesthouses_bp.route('/<int:guesthouse_id>/safety-assessment', methods=['GET'])
@jwt_required()
def get_safety_assessment(guesthouse_id):
    """
    Get comprehensive safety assessment for a guesthouse.
    This combines baseline safety, weather risks, and emergency facility access.
    
    Returns:
        200: Complete safety assessment
        403: Not authorized
        404: Guesthouse not found
    """
    current_owner_id = get_jwt_identity()
    
    guesthouse = Guesthouse.query.get(guesthouse_id)
    
    if not guesthouse:
        return jsonify({'error': 'Guesthouse not found'}), 404
    
    if int(guesthouse.owner_id) != int(current_owner_id):
        return jsonify({'error': 'Not authorized to access this guesthouse'}), 403
    
    try:
        # Create safety assessment
        assessment = SafetyAssessment(guesthouse)
        
        # Calculate baseline score
        baseline_result = assessment.calculate_baseline_score()
        
        # Get weather data and analysis
        weather_data = WeatherService.get_current_weather(
            guesthouse.latitude, 
            guesthouse.longitude
        )
        weather_analysis = WeatherService.analyze_weather_risks(weather_data)
        
        # Get nearby emergency facilities
        facilities_data = EmergencyFacilitiesService.find_nearby_facilities(
            guesthouse.latitude,
            guesthouse.longitude,
            radius_km=5
        )
        facilities_analysis = EmergencyFacilitiesService.analyze_facility_access(facilities_data)
        
        # Calculate final comprehensive score
        final_assessment = assessment.calculate_final_score(
            baseline_result,
            weather_analysis,
            facilities_analysis
        )
        
        # Add external data to response
        final_assessment['external_data'] = {
            'weather': weather_data,
            'emergency_facilities': facilities_data
        }
        
        return jsonify(final_assessment), 200
        
    except Exception as e:
        print(f"Assessment error: {e}")
        return jsonify({'error': 'Failed to generate safety assessment'}), 500