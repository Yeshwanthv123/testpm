#!/usr/bin/env python3
"""
Migration script to assign default regions to users without one.
This ensures users can appear in regional leaderboards.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal
from app.models import User

def migrate_regions():
    """Assign 'US' as default region to all users without one."""
    db = SessionLocal()
    try:
        # Get all users without a region
        users_without_region = db.query(User).filter(
            (User.region == None) | (User.region == '')
        ).all()
        
        if not users_without_region:
            print("✅ All users already have regions assigned!")
            return
        
        print(f"Found {len(users_without_region)} users without region assignments.")
        print(f"Assigning 'US' as default region...")
        
        # Assign 'US' as default
        for user in users_without_region:
            user.region = 'US'
        
        db.commit()
        print(f"✅ Successfully updated {len(users_without_region)} users with region 'US'")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    migrate_regions()
