from app import create_app
from app.models import db, Owner, Guesthouse

app = create_app()

with app.app_context():
    # Check owners
    print("\n" + "="*60)
    print("OWNERS IN DATABASE")
    print("="*60)
    owners = Owner.query.all()
    if owners:
        for owner in owners:
            print(f"\nID: {owner.id}")
            print(f"  Name: {owner.name}")
            print(f"  Email: {owner.email}")
            print(f"  Created: {owner.created_at}")
    else:
        print("No owners found")
    
    # Check guesthouses
    print("\n" + "="*60)
    print("GUESTHOUSES IN DATABASE")
    print("="*60)
    guesthouses = Guesthouse.query.all()
    if guesthouses:
        print(f"\nTotal guesthouses: {len(guesthouses)}\n")
        for gh in guesthouses:
            print(f"ID: {gh.id}")
            print(f"  Name: {gh.name}")
            print(f"  Owner ID: {gh.owner_id}")
            print(f"  Address: {gh.address}")
            print(f"  Building Type: {gh.building_type}")
            print(f"  Floors: {gh.number_of_floors}")
            print(f"  Rooms: {gh.number_of_rooms}")
            print(f"  Fire Extinguishers: {gh.fire_extinguishers}")
            print(f"  Smoke Detectors: {gh.smoke_detectors}")
            print(f"  Emergency Exits: {gh.emergency_exits}")
            print(f"  First Aid Kit: {gh.has_first_aid_kit}")
            print(f"  Stair Handrails: {gh.has_stair_handrails}")
            print(f"  Slip Resistant Stairs: {gh.stairs_slip_resistant}")
            print(f"  Created: {gh.created_at}")
            print()
    else:
        print("No guesthouses found")
    
    print("="*60)
