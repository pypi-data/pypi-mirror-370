from .geo_location_service import GeolocationService, GeocoderTimedOut, GeocoderServiceError

# Initialize the geolocator once
geolocator = None


def get_geolocator():
    """
    Provides a function to instantiate or retrieve a global geolocator instance
    using the GeolocationService class. If the geolocator has already been
    created, it will return the original global instance. Otherwise, it initializes
    a new instance of the GeolocationService with debugging enabled and stores it
    globally.

    :return: The global instance of the GeolocationService
    :rtype: GeolocationService
    """
    global geolocator
    if geolocator is None:
        geolocator = GeolocationService(debug=True)
    return geolocator


#geolocator = GeolocationService(debug=True)


def get_address_by_coordinates(latitude, longitude, exactly_one=True):
    """
    Retrieves the address based on the provided geographic coordinates (latitude and
    longitude). Utilizes the geopy library's geolocator to find and reverse-geocode
    the location associated with the given coordinates. Returns a human-readable
    address if available or an error message for specific conditions.

    :param latitude: The latitude of the location to find the address for.
    :type latitude: float
    :param longitude: The longitude of the location to find the address for.
    :type longitude: float
    :param exactly_one: If true, ensures exactly one result is returned. If false,
        returns a list of possible matches. Defaults to True.
    :type exactly_one: bool, optional
    :return: A string containing the human-readable address of the location or an
        error message in case of failure.
    :rtype: str
    """
    geolocator = get_geolocator()
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=exactly_one)
        if not location:
            return "No address found for this location."
        address = location.address
        return address
    except GeocoderTimedOut:
        return "GeocoderTimedOut: Failed to reach the server."


def get_coordinates_for_address(address):
    """
    Gets geographical coordinates (latitude and longitude) along with the full formatted
    address for a given address string. Makes use of a geolocation service to retrieve
    the data and handles possible exceptions during the process.

    :param address: The address as a string for which coordinates need to be determined.
    :type address: str

    :return: A dictionary containing the full formatted address, latitude, and longitude
             if the location is found. Otherwise, returns a string describing an error
             or that no location was found.
    :rtype: dict or str
    """
    geolocator = get_geolocator()
    try:
        location = geolocator.geocode(address)

        # Check if location was found
        if location:
            return {
                "Address": location.address,
                "Latitude": location.latitude,
                "Longitude": location.longitude
            }
        else:
            return "Location not found."

    except GeocoderTimedOut:
        return "GeocoderTimedOut: Request timed out."
    except GeocoderServiceError as e:
        return f"GeocoderServiceError: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
