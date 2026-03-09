"""Debug script to check box display issue."""

import logging
import sys
sys.path.insert(0, 'src')

from data.database import Database
from business.location_service import LocationService
from business.media_service import MediaService
from utils.config import DB_PATH

logging.basicConfig(level=logging.DEBUG)

# Initialize database
db = Database(DB_PATH)
location_service = LocationService(db)
media_service = MediaService(db)

# Get all locations
locations = location_service.get_all_locations()
print("\n=== LOCATIONS ===")
for loc in locations:
    print(f"ID={loc.id}, Box={loc.box}, Place={loc.place}")

# Get all media
media_list = media_service.get_all_media()
print("\n=== MEDIA (first 10) ===")
for media in media_list[:10]:
    if media.location_id:
        # Find the location
        loc = next((l for l in locations if l.id == media.location_id), None)
        if loc:
            print(f"Media ID={media.id}, Name={media.name}, location_id={media.location_id}, Box from location={loc.box}")
        else:
            print(f"Media ID={media.id}, Name={media.name}, location_id={media.location_id}, Location NOT FOUND")
    else:
        print(f"Media ID={media.id}, Name={media.name}, location_id=None")

db.close()
