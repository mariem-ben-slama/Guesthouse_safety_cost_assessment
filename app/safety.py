from flask import current_app
from datetime import datetime

class SafetyAssessment:
    """
    Enhanced safety assessment with comprehensive cost estimation.
    Provides realistic project costs including equipment, installation, compliance, and maintenance.
    """
    
    def __init__(self, guesthouse):
        """
        Initialize with a guesthouse object.
        
        Args:
            guesthouse: Guesthouse database model instance
        """
        self.guesthouse = guesthouse
        self.config = current_app.config
        self.thresholds = self.config['SAFETY_THRESHOLDS']
        
        # Load cost structures
        self.equipment_costs = self.config['EQUIPMENT_COSTS']
        self.installation_costs = self.config['INSTALLATION_COSTS']
        self.compliance_costs = self.config['COMPLIANCE_COSTS']
        self.maintenance_costs = self.config['MAINTENANCE_COSTS']
        self.optional_improvements = self.config['OPTIONAL_IMPROVEMENTS']
        
        # Building type multiplier for installation complexity
        building_type = getattr(guesthouse, 'building_type', 'traditional') or 'traditional'
        self.building_multiplier = self.config['BUILDING_TYPE_MULTIPLIERS'].get(building_type, 1.0)
    
    def calculate_baseline_score(self):
        """
        Calculate baseline safety score with comprehensive cost breakdown.
        
        Returns:
            dict with score, issues, recommendations, and detailed cost estimates
        """
        score = 100  # Start with perfect score
        issues = []
        recommendations = []
        
        # Cost categories
        equipment_cost = 0
        installation_cost = 0
        compliance_cost = 0
        annual_maintenance = 0
        
        # Track what needs to be added for cost calculation
        items_to_add = {
            'fire_extinguishers': 0,
            'smoke_detectors': 0,
            'emergency_exits': 0,
            'first_aid_kit': False,
            'handrails': 0,
            'slip_coating': False
        }
        
        # 1. Check building age
        current_year = datetime.now().year
        building_age = current_year - self.guesthouse.construction_year
        
        if self.guesthouse.construction_year < self.thresholds['old_building_year']:
            score -= 10
            issues.append(f'Building is {building_age} years old (built before {self.thresholds["old_building_year"]})')
            recommendations.append('Consider professional structural inspection for older buildings')
        
        # 2. Check fire extinguishers
        required_extinguishers = self.guesthouse.number_of_floors * self.thresholds['min_fire_extinguishers_per_floor']
        extinguisher_deficit = max(0, required_extinguishers - self.guesthouse.fire_extinguishers)
        
        if extinguisher_deficit > 0:
            score -= extinguisher_deficit * 5
            issues.append(f'Need {extinguisher_deficit} more fire extinguisher(s)')
            recommendations.append(f'Add {extinguisher_deficit} fire extinguisher(s) (minimum one per floor)')
            items_to_add['fire_extinguishers'] = extinguisher_deficit
        
        # 3. Check smoke detectors
        required_detectors = self.guesthouse.number_of_floors * self.thresholds['min_smoke_detectors_per_floor']
        detector_deficit = max(0, required_detectors - self.guesthouse.smoke_detectors)
        
        if detector_deficit > 0:
            score -= detector_deficit * 4
            issues.append(f'Need {detector_deficit} more smoke detector(s)')
            recommendations.append(f'Install {detector_deficit} smoke detector(s) (minimum {self.thresholds["min_smoke_detectors_per_floor"]} per floor)')
            items_to_add['smoke_detectors'] = detector_deficit
        
        # 4. Check emergency exits
        exit_deficit = max(0, self.thresholds['min_emergency_exits'] - self.guesthouse.emergency_exits)
        
        if exit_deficit > 0:
            score -= exit_deficit * 10
            issues.append(f'Need {exit_deficit} more emergency exit(s)')
            recommendations.append(f'Add {exit_deficit} clearly marked emergency exit(s) with illuminated signs')
            items_to_add['emergency_exits'] = exit_deficit
        
        # 5. Check first aid kit
        if not self.guesthouse.has_first_aid_kit:
            score -= 8
            issues.append('No first aid kit available')
            recommendations.append('Provide a well-stocked first aid kit in an accessible location')
            items_to_add['first_aid_kit'] = True
        
        # 6. Check stair safety (if multi-floor building)
        if self.guesthouse.number_of_floors > 1:
            if not self.guesthouse.has_stair_handrails:
                score -= 8
                issues.append('Stairs lack handrails')
                recommendations.append('Install handrails on all staircases')
                items_to_add['handrails'] = self.guesthouse.number_of_floors - 1
            
            if not self.guesthouse.stairs_slip_resistant:
                score -= 6
                issues.append('Stairs are not slip-resistant')
                recommendations.append('Apply slip-resistant coating or install anti-slip strips on stairs')
                items_to_add['slip_coating'] = True
        
        # Calculate equipment costs
        equipment_cost += items_to_add['fire_extinguishers'] * self.equipment_costs['fire_extinguisher']
        equipment_cost += items_to_add['smoke_detectors'] * self.equipment_costs['smoke_detector']
        equipment_cost += items_to_add['emergency_exits'] * self.equipment_costs['emergency_exit_sign']
        if items_to_add['first_aid_kit']:
            equipment_cost += self.equipment_costs['first_aid_kit']
        if items_to_add['handrails'] > 0:
            # Assume 3.5 meters average per staircase
            equipment_cost += items_to_add['handrails'] * self.equipment_costs['stair_handrail'] * 3.5
        if items_to_add['slip_coating']:
            equipment_cost += items_to_add['handrails'] * self.equipment_costs['slip_resistant_coating'] if items_to_add['handrails'] > 0 else self.equipment_costs['slip_resistant_coating']
        
        # Calculate installation costs (with building type multiplier)
        base_installation = 0
        base_installation += items_to_add['fire_extinguishers'] * self.installation_costs['fire_extinguisher']
        base_installation += items_to_add['smoke_detectors'] * self.installation_costs['smoke_detector']
        base_installation += items_to_add['emergency_exits'] * self.installation_costs['emergency_exit_sign']
        if items_to_add['handrails'] > 0:
            base_installation += items_to_add['handrails'] * self.installation_costs['stair_handrail'] * 3.5
        if items_to_add['slip_coating']:
            base_installation += items_to_add['handrails'] * self.installation_costs['slip_resistant_coating'] if items_to_add['handrails'] > 0 else self.installation_costs['slip_resistant_coating']
        
        installation_cost = round(base_installation * self.building_multiplier)
        
        # Calculate compliance costs (only if improvements are needed)
        if equipment_cost > 0:
            # Initial fire safety inspection required
            compliance_cost += self.compliance_costs['fire_safety_inspection']
            # Safety certification after improvements
            compliance_cost += self.compliance_costs['safety_certification']
        
        # Calculate annual maintenance costs for existing + new equipment
        total_extinguishers = self.guesthouse.fire_extinguishers + items_to_add['fire_extinguishers']
        total_detectors = self.guesthouse.smoke_detectors + items_to_add['smoke_detectors']
        total_exits = self.guesthouse.emergency_exits + items_to_add['emergency_exits']
        
        annual_maintenance += total_extinguishers * self.maintenance_costs['fire_extinguisher']
        annual_maintenance += total_detectors * self.maintenance_costs['smoke_detector']
        annual_maintenance += total_exits * self.maintenance_costs['emergency_exit_sign']
        if self.guesthouse.has_first_aid_kit or items_to_add['first_aid_kit']:
            annual_maintenance += self.maintenance_costs['first_aid_kit']
        if self.guesthouse.has_stair_handrails or items_to_add['handrails'] > 0:
            handrail_count = items_to_add['handrails'] if items_to_add['handrails'] > 0 else (self.guesthouse.number_of_floors - 1)
            annual_maintenance += handrail_count * self.maintenance_costs['stair_handrail']
        
        # Add annual fire inspection
        annual_maintenance += self.compliance_costs['annual_fire_inspection']
        
        # Calculate optional improvements (recommendations only)
        optional_recommendations = self._generate_optional_recommendations()
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        # Determine risk level
        if score >= 80:
            risk_level = 'low'
        elif score >= 50:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'baseline_score': score,
            'risk_level': risk_level,
            'issues': issues if issues else ['No major safety issues detected'],
            'recommendations': recommendations if recommendations else ['Guesthouse meets baseline safety standards'],
            'cost_breakdown': {
                'equipment': round(equipment_cost),
                'installation_labor': installation_cost,
                'compliance_inspection': compliance_cost,
                'total_one_time': round(equipment_cost + installation_cost + compliance_cost),
                'annual_maintenance': round(annual_maintenance)
            },
            'optional_improvements': optional_recommendations,
            'building_notes': self._get_building_notes()
        }
    
    def _generate_optional_recommendations(self):
        """
        Generate optional safety improvement recommendations based on guesthouse characteristics.
        These are nice-to-have enhancements, not mandatory.
        """
        optional = []
        
        # Fire blanket for kitchen safety (recommended for all)
        optional.append({
            'item': 'Fire blanket',
            'reason': 'Kitchen fire suppression',
            'cost_tnd': self.optional_improvements['fire_blanket']
        })
        
        # Emergency lighting for multi-floor buildings
        if self.guesthouse.number_of_floors > 1:
            optional.append({
                'item': 'Emergency lighting',
                'reason': 'Battery backup lighting for safe evacuation during power outages',
                'cost_tnd': self.optional_improvements['emergency_lighting'] * self.guesthouse.number_of_floors
            })
        
        # Carbon monoxide detector (if kitchen present - assume yes for guesthouses)
        optional.append({
            'item': 'Carbon monoxide detector',
            'reason': 'Detect dangerous gas from cooking appliances or heating',
            'cost_tnd': self.optional_improvements['carbon_monoxide_detector']
        })
        
        # Fire alarm system for larger properties
        if self.guesthouse.number_of_rooms >= 6:
            optional.append({
                'item': 'Centralized fire alarm system',
                'reason': 'Comprehensive alert system for larger properties',
                'cost_tnd': self.optional_improvements['fire_alarm_system']
            })
        
        # Emergency evacuation plan
        if self.guesthouse.number_of_floors > 1 or self.guesthouse.number_of_rooms >= 5:
            optional.append({
                'item': 'Emergency evacuation plan signage',
                'reason': 'Professional floor plans and evacuation route markers',
                'cost_tnd': self.optional_improvements['emergency_evacuation_plan']
            })
        
        # Security cameras (recommended for guest safety)
        if self.guesthouse.number_of_rooms >= 4:
            camera_count = 2  # Entrance + common area
            optional.append({
                'item': f'{camera_count} security cameras',
                'reason': 'Monitor entrance and common areas for guest security',
                'cost_tnd': self.optional_improvements['security_camera'] * camera_count
            })
        
        return optional
    
    def _get_building_notes(self):
        """Generate context-specific notes about building characteristics."""
        notes = []
        
        building_type = getattr(self.guesthouse, 'building_type', 'traditional') or 'traditional'
        
        if building_type == 'traditional':
            notes.append('Traditional construction: Installation may require specialized techniques for stone/masonry walls')
        elif building_type == 'modern':
            notes.append('Modern construction: Standard installation procedures apply, slightly lower labor costs')
        elif building_type == 'renovated':
            notes.append('Renovated building: Mixed construction may require varied installation approaches')
        
        if self.guesthouse.construction_year < 1980:
            notes.append('Pre-1980 construction: Strongly recommend professional structural assessment')
        
        if self.guesthouse.number_of_floors >= 3:
            notes.append('Multi-floor building: Consider additional fire safety measures and clear evacuation routes')
        
        if self.guesthouse.number_of_rooms >= 8:
            notes.append('Larger property: May benefit from centralized fire alarm system')
        
        return notes
    
    def calculate_final_score(self, baseline_result, weather_analysis, facilities_analysis):
        """
        Calculate final daily risk score combining baseline, weather, and facilities data.
        
        Args:
            baseline_result: Result from calculate_baseline_score()
            weather_analysis: Result from WeatherService.analyze_weather_risks()
            facilities_analysis: Result from EmergencyFacilitiesService.analyze_facility_access()
            
        Returns:
            dict with comprehensive safety assessment and cost breakdown
        """
        # Start with baseline score
        final_score = baseline_result['baseline_score']
        
        # Adjust for weather risks (temporary, daily factor)
        weather_risk = weather_analysis.get('risk_score', 0)
        final_score -= weather_risk
        
        # Adjust for facility access (reduced impact - divide by 2)
        facility_risk = facilities_analysis.get('risk_adjustment', 0)
        final_score -= (facility_risk / 2)
        
        # Ensure score stays within 0-100 range
        final_score = max(0, min(100, final_score))
        
        # Determine final risk level
        if final_score >= 80:
            final_risk_level = 'low'
        elif final_score >= 50:
            final_risk_level = 'medium'
        else:
            final_risk_level = 'high'
        
        # Combine all recommendations
        all_recommendations = {
            'mandatory_improvements': baseline_result['recommendations'],
            'facilities_access': facilities_analysis.get('recommendations', []),
            'weather_today': weather_analysis.get('recommendations', []),
            'optional_enhancements': baseline_result['optional_improvements']
        }
        
        # Calculate total investment summary
        one_time_cost = baseline_result['cost_breakdown']['total_one_time']
        annual_cost = baseline_result['cost_breakdown']['annual_maintenance']
        
        # Optional improvements total
        optional_total = sum(item['cost_tnd'] for item in baseline_result['optional_improvements'])
        
        return {
            'guesthouse_id': self.guesthouse.id,
            'guesthouse_name': self.guesthouse.name,
            'assessment_date': datetime.now().isoformat(),
            'scores': {
                'baseline_score': baseline_result['baseline_score'],
                'baseline_risk_level': baseline_result['risk_level'],
                'weather_risk_score': weather_risk,
                'facility_risk_adjustment': facility_risk,
                'final_score': round(final_score, 1),
                'final_risk_level': final_risk_level
            },
            'issues_identified': baseline_result['issues'],
            'recommendations': all_recommendations,
            'cost_estimates': {
                'mandatory_improvements': {
                    'equipment_materials': baseline_result['cost_breakdown']['equipment'],
                    'installation_labor': baseline_result['cost_breakdown']['installation_labor'],
                    'compliance_inspections': baseline_result['cost_breakdown']['compliance_inspection'],
                    'total_one_time_investment': one_time_cost,
                    'currency': 'TND'
                },
                'ongoing_costs': {
                    'annual_maintenance': annual_cost,
                    'description': 'Equipment servicing, inspections, and supply restocking',
                    'currency': 'TND'
                },
                'optional_improvements': {
                    'total_if_all_implemented': optional_total,
                    'items': baseline_result['optional_improvements'],
                    'note': 'These are recommended enhancements, not mandatory requirements',
                    'currency': 'TND'
                },
                'project_summary': {
                    'minimum_investment': one_time_cost,
                    'with_optional_improvements': one_time_cost + optional_total,
                    'first_year_total': one_time_cost + annual_cost,
                    'currency': 'TND'
                }
            },
            'building_context': {
                'type': getattr(self.guesthouse, 'building_type', 'traditional'),
                'installation_complexity': self._complexity_description(),
                'notes': baseline_result['building_notes']
            },
            'explanation': self._generate_explanation(
                final_score,
                baseline_result,
                weather_analysis,
                facilities_analysis,
                one_time_cost,
                annual_cost
            )
        }
    
    def _complexity_description(self):
        """Return human-readable installation complexity description."""
        if self.building_multiplier < 1.0:
            return 'Lower complexity (modern construction, easier installation)'
        elif self.building_multiplier > 1.0:
            return 'Higher complexity (renovated structure, varied installation requirements)'
        else:
            return 'Standard complexity (traditional construction)'
    
    def _generate_explanation(self, final_score, baseline, weather, facilities, one_time_cost, annual_cost):
        """
        Generate comprehensive human-readable explanation of the assessment.
        
        Returns:
            string with detailed explanation
        """
        explanation = f"Your guesthouse received a final safety score of {round(final_score, 1)}/100 ({self._score_to_text(final_score)}). "
        
        # Baseline explanation
        baseline_score = baseline['baseline_score']
        explanation += f"The baseline safety score is {baseline_score}/100 based on your building's safety equipment and structure. "
        
        if baseline['issues']:
            explanation += f"We identified {len(baseline['issues'])} area(s) requiring improvement. "
        else:
            explanation += "Your baseline safety standards are excellent. "
        
        # Cost breakdown explanation
        if one_time_cost > 0:
            explanation += f"The total one-time investment for mandatory improvements is {one_time_cost} TND, which includes equipment ({baseline['cost_breakdown']['equipment']} TND), installation labor ({baseline['cost_breakdown']['installation_labor']} TND), and compliance inspections ({baseline['cost_breakdown']['compliance_inspection']} TND). "
        else:
            explanation += "No mandatory improvements are needed. "
        
        if annual_cost > 0:
            explanation += f"Ongoing annual maintenance costs are estimated at {annual_cost} TND for equipment servicing, inspections, and supply restocking. "
        
        # Weather impact
        weather_risk = weather.get('risk_score', 0)
        if weather_risk > 0:
            explanation += f"Today's weather conditions add {weather_risk} risk points. "
        else:
            explanation += "Weather conditions today pose minimal risk. "
        
        # Facilities impact
        facility_risk = facilities.get('risk_adjustment', 0)
        if facility_risk > 10:
            explanation += f"Limited access to emergency facilities adds {round(facility_risk/2)} risk points to your daily score. "
        else:
            explanation += "Good access to emergency facilities in your area. "
        
        # Optional improvements note
        if baseline['optional_improvements']:
            explanation += f"Additionally, {len(baseline['optional_improvements'])} optional safety enhancements are recommended to further improve guest safety and comfort."
        
        return explanation
    
    def _score_to_text(self, score):
        """Convert numerical score to text description."""
        if score >= 80:
            return "Low Risk"
        elif score >= 50:
            return "Medium Risk"
        else:
            return "High Risk"