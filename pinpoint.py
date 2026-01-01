from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from config import TARGET_REGION, ALERT_CALIFORNIA_CAMERAS, CAMERA_CHECK_RADIUS_KM

class WildfirePinpointer:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="wildfire_pipeline_v3")

    def get_lat_long(self, location_name):
        try:
            query = f"{location_name}, {TARGET_REGION}"
            location = self.geolocator.geocode(query, timeout=5)
            if location:
                return location.latitude, location.longitude
            return None, None
        except Exception:
            return None, None

    def verify_with_cameras(self, lat, lon):
        """
        Checks if the coordinates are within X km of a known ALERTCalifornia camera.
        Returns (Verified (Bool), Nearest Camera Coords)
        """
        if not lat or not lon: return False, None
        
        event_point = (lat, lon)
        for cam_lat, cam_lon in ALERT_CALIFORNIA_CAMERAS:
            cam_point = (cam_lat, cam_lon)
            distance = geodesic(event_point, cam_point).km
            if distance <= CAMERA_CHECK_RADIUS_KM:
                return True, cam_point
        
        return False, None
