"""
:class:`.GoogleAPI` geocoder.
:autthor@ksodari
"""
import re
from datetime import timedelta

import requests

from decouple import config

API_KEY = config('GOOGLE_API_KEY')

# Google Maps API URL Format
API_URL = "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,\
                                                           +CA&key=%s" % API_KEY

__all__ = (
    "DEFAULT_SCHEME",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRY_TIMEOUT",
)

DEFAULT_SCHEME = 'https'
DEFAULT_TIMEOUT = None
DEFAULT_RETRY_TIMEOUT = 60
DEFAULT_QUERIES_PER_SECOND = 50


class GoogleMapApi():
    """
    Geocoder using the Google Maps Locations API. Documentation at:
        https://developers.google.com/maps/documentation/geocoding/start
    """
    # default api_endpoint
    api_url = "https://maps.googleapis.com/maps/api/geocode/json"
    api_key = None
    structured_query_params = {
        'street',
        'city',
        'state',
        'zipCode',
        'postalCode',
    }

    def __init__(self, api_key, client_id=None, client_secret=None,
                 scheme=DEFAULT_SCHEME, timeout=DEFAULT_TIMEOUT,
                 retry_timeout=DEFAULT_RETRY_TIMEOUT,
                 ):
        """Initialize a customized Google geocoder with location-specific
        address information and your Bing Maps API key.

        :param api_key: Maps API key. Required, unless "client_id" and
            "client_secret" are set.
        :type api_key: string
        :param client_id: (for Maps API for Work customers) Your client ID.
        :type client_id: string
        :param client_secret: (for Maps API for Work customers) Your client
            secret (base64 encoded).
        :type client_secret: string
        :param channel: (for Maps API for Work customers) When set, a channel
            parameter with this value will be added to the requests.
            This can be used for tracking purpose.
            Can only be used with a Maps API client ID.
        :type channel: str
        :param timeout: Combined connect and read timeout for HTTP requests, in
            seconds. Specify "None" for no timeout.
        :type timeout: int

        """
        if not api_key and not (client_secret and client_id):
            raise ValueError("Must provide API key or enterprise credentials "
                             "when creating client.")

        if api_key and not api_key.startswith("AIza"):
            raise ValueError("Invalid API key provided.")

        """
        if channel:
            if not client_id:
                raise ValueError("The channel argument must be used with a "
                                 "client ID")
            if not re.match("^[a-zA-Z0-9._-]*$", channel):
                raise ValueError("The channel argument must be an ASCII "
                                 "alphanumeric string. The period (.), underscore (_)"
                                 "and hyphen (-) characters are allowed.")
        """
        # self.session = requests.Session()
        # self.channel = channel
        # Note: For later use-case
        # super(GoogleMapApi, self).__init__(scheme, timeout, retry_timeout, channel=channel)
        self.timeout = timeout
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.api_url = "{}://maps.googleapis.com/maps/api/geocode/json".format(scheme)

    def find_geocode(self, address):
        """
        Geocode and address/location
        :param address: The address or location query to geocode.
        :return: latitude and longitude values

        """
        # check if the address is sent as dict format
        if isinstance(address, dict):
            address = ", ".join(address.values())

        # defining a params dict for the parameters to be sent to the API
        PARAMS = {
            'address': address,
            'key': self.api_key,
        }

        direct_url = "{0}?address={1}&key={2}".format(self.api_url, address, self.api_key)
        # response = requests.get(url=self.api_url, params=PARAMS)

        # sending get request and saving the response as response object
        response = requests.get(url=self.api_url, params=PARAMS)

        # extracting data in json format and get the result from json value
        data = response.json().get('results')[0]

        # extracting latitude, longitude and formatted address
        # of the first matching location
        latitude = data.get('geometry').get('location').get('lat')
        longitude = data.get('geometry').get('location').get('lng')
        formatted_address = data.get('formatted_address')
        postal_code = data.get('address_components')[-1].get('short_name')

        # context to return
        context = {'lat': latitude, 'lng': longitude, 'postalCode': postal_code, 'address': formatted_address}

        # printing the output
        print("Latitude: {}\nLongitude: {}\nFormatted Address: {}".format(latitude, longitude, formatted_address))

        return data or context

    def reverse_geocode(self, latlng):

        # if latlng is sent as list item
        if isinstance(latlng, list):
            if latlng.__len__() != 2:
                raise ValueError("Invalid latlng values. The list must be of length 2 with latitude and longitude "
                                 "values only.")
            latlng = "{}, {}".format(latlng[0], latlng[1])

        # if latlng is a dictionary formatted data
        if isinstance(latlng, dict):
            if not ({'latitude', 'longitude', 'lat', 'lng'} >= latlng.keys()):
                raise ValueError("Invalid format. The dict must be of length 2 with key as 'latitude' or 'lat' and "
                                 "'longitude' or 'lng' only.")
            latlng = "{}, {}".format(latlng.get('lat', latlng.get('latitude')), latlng.get('lng', latlng.get(
                'longitude')))

        # check if latlng is a tuple formatted data
        if isinstance(latlng, tuple):
            if latlng.__len__() != 2:
                raise ValueError("Invalid latlng values. The tuple must be of length 2 with latitude and longitude "
                                 "values only formatted as (lat, lng).")
            latlng = "{}, {}".format(latlng[0], latlng[1])

        # defining a params dict for the parameters to be sent to the API URL
        PARAMS = {
            'latlng': latlng,
            'key': self.api_key,
        }

        # sample_url = https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=YOUR_API_KEY
        # sending get request and saving the response as response object
        response = requests.get(url=self.api_url, params=PARAMS)

        # extracting data in json format and get the result from json value
        data = response.json().get('results')[0]

        # extracting latitude, longitude and formatted address of the first matching location
        latitude = data.get('geometry').get('location').get('lat')
        longitude = data.get('geometry').get('location').get('lng')
        formatted_address = data.get('formatted_address')
        postal_code = data.get('address_components')[-1].get('short_name')

        # printing the output
        print("Latitude: {}\nLongitude: {}\nFormatted Address: {}".format(latitude, longitude, formatted_address))
        # context to return
        context = {'lat': latitude, 'lng': longitude, 'postalCode': postal_code, 'address': formatted_address}

        return data
