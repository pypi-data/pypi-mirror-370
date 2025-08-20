import os
from urllib.parse import urlparse
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

app_nominatim_url = os.environ.get('NOMINATIM_URL', None)
app_geo_locator_test_place = os.environ.get('GEO_LOCATOR_TEST_PLACE', "San Jose, Costa Rica")


class GeolocationService:
    """
    Provides geolocation services, such as forward and reverse geocoding.

    This class is intended to interface with a geocoding service (e.g., Nominatim)
    for performing geocoding operations. It initializes the geolocation service
    based on a provided or default configuration and provides methods for geocoding
    addresses or retrieving addresses from coordinates.

    :ivar geolocator: Instance of the geocoding service used for geolocation tasks.
        Will be `None` if initialization fails or is incomplete.
    :type geolocator: Optional[Nominatim]
    :ivar debug: Indicates whether debug messages are enabled.
    :type debug: bool
    """
    debug: bool = False

    def __init__(self, debug=False):
        self.geolocator = None
        self._initialize_geolocator()
        self.debug = debug

    def _initialize_geolocator(self):
        nominatim_url = app_nominatim_url
        if not nominatim_url:
            if self.debug:
                print("Nominatim URL not provided in environment variables.")
            return

        try:
            parsed_url = urlparse(nominatim_url)
            nominatim_url = parsed_url.netloc
            self.geolocator = Nominatim(user_agent="ibis", scheme="http", domain=nominatim_url)

            # Test the geolocator to ensure it is available
            location = self.geolocator.geocode(app_geo_locator_test_place)
            if location:
                if self.debug:
                    print("Geolocator is available.")
            else:
                if self.debug:
                    print("Geolocator service is not responding correctly.")
                self.geolocator = None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error initializing geolocator: {e}")
            self.geolocator = None

    def geocode(self, address):
        if not self.geolocator:
            if self.debug:
                print("Geolocator is not available.")
            return None
        try:
            return self.geolocator.geocode(address)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error during geocoding: {e}")
            return None

    def reverse(self, coordinates, exactly_one=True):
        if not self.geolocator:
            if self.debug:
                print("Geolocator is not available.")
            return None
        try:
            return self.geolocator.reverse(coordinates, exactly_one=exactly_one)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error during reverse geocoding: {e}")
            return None
