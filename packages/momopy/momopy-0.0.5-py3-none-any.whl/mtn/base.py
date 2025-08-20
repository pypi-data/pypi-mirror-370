import requests
import uuid
import mtn as mtnapi
from mtn.utils.exceptions import MoMoAPIError
from mtn.utils.logger import logger

class Borg:
    """
    Borg class making class attributes global.
    Implements the Borg design pattern which allows all instances to share state.
    """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Base(Borg):
    """
    Base Class used across defined.
    This class initializes the MTN MoMo API with the provided secret key.
    
    Attributes:
        requests (MomoBaseRequests): An instance of the MomoBaseRequests class for making API requests.
    """

    def __init__(self, token=None, **kwargs):
        """
        Initialize MTN MoMo with required credentials.
        """
        # super().__init__()
        Borg.__init__(self)

        
        base_url = kwargs.get('base_url', mtnapi.BASE_API_URL)
        environment = kwargs.get('environment', mtnapi.ENVIRONMENT)
        callback_host = kwargs.get('callback_host', mtnapi.CALLBACK_HOST)
        
        api_user = kwargs.get('api_user', mtnapi.PRODUCT_API_USER_ID)
        api_key = kwargs.get('api_key', mtnapi.PRODUCT_API_SECRET)
        subscription_key = kwargs.get('subscription_key', mtnapi.PRODUCT_SUBSCRIPTION_KEY)

        auth_str = f'{api_user}:{api_key}'
        # auth_bytes = auth_str.encode('utf-8')
        # auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': subscription_key,
            'X-Target-Environment': environment,
            # 'X-Callback-Url': callback_host,
        }
                
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        arguments = dict(base_url=base_url, headers=headers)
        if not hasattr(self, 'requests'):
            req = MomoBaseRequests(**arguments)
            self._shared_state.update(requests=req)
        else:
            self.requests.headers.update(headers)

class MomoBaseRequests:
    """
    Handles HTTP requests to the MTN MoMo API.
    
    Args:
        base_url (str): The base URL for the MoMo API.
        environment (str): The environment to use (sandbox or live).
        callback_host (str): The callback host URL.
    """

    def __init__(self, base_url, headers=None):
        self.BASE_API_URL = base_url
        self.headers = headers

    def _request(self, method, resource_uri, **kwargs):
        full_url = self.BASE_API_URL + resource_uri
        
        headers = self.headers.copy()  # Create a copy of the headers

        # Add X-Reference-Id for POST requests
        if method == requests.post:
            headers['X-Reference-Id'] = str(uuid.uuid4())
            
        logger.info(f"Making {method.__name__.upper()} request to: {full_url}")
        # logger.info(f"Headers: {headers}")
        # logger.info(f"kwargs: {kwargs}")
        
        """
        Perform a HTTP request on a resource.

        Args:
            method (function): HTTP method from requests (e.g., requests.get, requests.post).
            resource_uri (str): The endpoint of the resource.
            headers (dict): Headers for the request.

        Keyword Args:
            data (dict, optional): JSON data to send in the body of the request.
            params (dict, optional): Query parameters to include in the URL.

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.

        Returns:
            dict: The JSON response from the API.
        """
            
        data = kwargs.get("data")
        params = kwargs.get("params")

        try:
            response = method(
                self.BASE_API_URL + resource_uri,
                json=data,
                headers=headers,                    # Use the updated headers with X-Reference-Id
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # Log raw response content if JSON parsing fails
            error_detail = response.text if response.content else "No content"
            logger.error(f"HTTP error occurred: {http_err}")
            logger.error(f"Status Code: {response.status_code}")
            logger.error(f"Response Content: {error_detail}")
            raise MoMoAPIError(
                status_code=response.status_code,
                error_message=str(http_err),
                details=error_detail
            ) from http_err
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred: {req_err}")
            logger.error(f"Response Content: {response.text if response.content else 'No content'}")
            raise MoMoAPIError(
                status_code=None,
                error_message="Request failed",
                details=str(req_err)
            ) from req_err


    def get(self, endpoint, **kwargs):
        """
        Send a GET request to a resource.

        Args:
            endpoint (str): The endpoint of the resource.
            primary_key (str): Subscription primary key.

        Keyword Args:
            params (dict, optional): Query parameters to include in the URL.

        Returns:
            dict: The JSON response from the API.
        """
        return self._request(requests.get, endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        """
        Send a POST request to create a resource.

        Args:
            endpoint (str): The endpoint of the resource.
            primary_key (str): Subscription primary key.
        
        Keyword Args:
            data (dict, optional): JSON data to send in the body of the request.

        Returns:
            dict: The JSON response from the API.
        """
        return self._request(requests.post, endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        """
        Send a PUT request to update a resource.

        Args:
            endpoint (str): The endpoint of the resource.
            primary_key (str): Subscription primary key.
        
        Keyword Args:
            data (dict, optional): JSON data to send in the body of the request.

        Returns:
            dict: The JSON response from the API.
        """
        return self._request(requests.put, endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        """
        Send a DELETE request to remove a resource.

        Args:
            endpoint (str): The endpoint of the resource.
            primary_key (str): Subscription primary key.

        Keyword Args:
            params (dict, optional): Query parameters to include in the URL.

        Returns:
            dict: The JSON response from the API indicating the result of the delete operation.

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.
        """
        return self._request(requests.delete, endpoint, **kwargs)
