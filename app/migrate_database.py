"""
Database Migration Script
Adds building_type column to existing guesthouses table.
Run this once after updating the models.
"""

import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from sqlalchemy import text

def migrate():
    """Add building_type column if it doesn't exist."""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(
                text("SELECT COUNT(*) FROM pragma_table_info('guesthouses') WHERE name='building_type'")
            )
            exists = result.scalar() > 0
            
            if not exists:
                print("Adding building_type column to guesthouses table...")
                db.session.execute(
                    text("ALTER TABLE guesthouses ADD COLUMN building_type VARCHAR(20) DEFAULT 'traditional'")
                )
                db.session.commit()
                print("✓ Column added successfully!")
                
                # Update existing records
                db.session.execute(
                    text("UPDATE guesthouses SET building_type = 'traditional' WHERE building_type IS NULL")
                )
                db.session.commit()
                print("✓ Existing records updated with default value 'traditional'")
            else:
                print("✓ Column building_type already exists. No migration needed.")
                
        except Exception as e:
            print(f"✗ Migration error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()