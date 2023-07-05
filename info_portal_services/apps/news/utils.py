import json
from rest_framework.exceptions import ParseError

def validate_location(location):
    if location and isinstance(location, str):
        try:
            location = json.loads(location)
        except ValueError:
            raise ParseError(detail="Invalid location")
    return location