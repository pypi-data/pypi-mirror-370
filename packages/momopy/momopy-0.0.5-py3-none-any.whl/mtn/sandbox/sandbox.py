import uuid
import requests
import os
from mtn.base import Base
import mtn
import base64
from mtn.utils.logger import logger

class Sandbox(Base):
    """
    Sandbox class for interacting with MTN MoMo Sandbox API.

    This class provides methods to create an API user, generate an API key,
    and generate a token for Bearer authentication using the MTN MoMo Sandbox API.

    Attributes:
        None
    """

    @staticmethod
    def create_api_user(subscription_key):
        """
        Create an API user in the MTN MoMo Sandbox environment.

        Args:
            subscription_key (str): The subscription key provided by MTN MoMo.

        Returns:
            dict: JSON data from MTN MoMo API containing the details of the created API user.

        Raises:
            HTTPError: If the request to create the API user fails.
        """
        headers = {
            'X-Reference-Id': str(uuid.uuid4()),
            'Ocp-Apim-Subscription-Key': subscription_key,
        }
        data = {
            'providerCallbackHost': os.getenv('CALLBACK_HOST')
        }
        try:
            response = requests.post(f'{mtn.BASE_API_URL}/v1_0/apiuser', headers=headers, json=data)
            response.raise_for_status()
                        
            # Since the response does not contain JSON data, return a success message or None
            logger.info(f"X-Reference-Id: {headers['X-Reference-Id']}")
            if response.status_code == 201:
                return {
                    'referenceId': headers['X-Reference-Id'],
                    'message': 'API user created successfully'
                }
            return None
        except requests.HTTPError as e:
            logger.error(f"Failed to create API user: {e}")
            raise
    
    @staticmethod
    def generate_api_key(reference_id, subscription_key):
        """
        Generate an API key for the created API user.

        Args:
            reference_id (str): The reference ID of the created API user.
            subscription_key (str): The subscription key provided by MTN MoMo.

        Returns:
            dict: JSON data from MTN MoMo API containing the generated API key.

        Raises:
            HTTPError: If the request to generate the API key fails.
        """
        headers = {
            'X-Reference-Id': reference_id,
            'Ocp-Apim-Subscription-Key': subscription_key,
        }
        try:
            response = requests.post(f'{mtn.BASE_API_URL}/v1_0/apiuser/{reference_id}/apikey', headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"Failed to generate API key: {e}")
            raise

    @staticmethod
    def generate_token(api_user, api_key, product, subscription_key):
        """
        Generate a token for Bearer authentication for a specific product.

        Args:
            api_user (str): The API user ID.
            api_key (str): The generated API key.
            product (str): The product for which to generate the token (e.g., 'disbursement', 'remittance').

        Returns:
            dict: JSON data from MTN MoMo API containing the Bearer token.

        Raises:
            HTTPError: If the request to generate the token fails.
        """
        product_endpoints = {
            'disbursement': 'disbursement/token/',
            'remittance': 'remittance/token/',
            'collection': 'collection/token/',
        }
        endpoint = product_endpoints.get(product)
        if not endpoint:
            raise ValueError(f"Invalid product specified: {product}")

        auth_str = f'{api_user}:{api_key}'
        auth_bytes = auth_str.encode('utf-8')
        auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Ocp-Apim-Subscription-Key': subscription_key,
        }
        try:
            response = requests.post(f'{mtn.BASE_API_URL}/{endpoint}', headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error(f"Failed to generate token: {e}")
            raise

    @classmethod
    def get_token(cls, subscription_key, product):
        """
        Create API user, generate API key, and obtain Bearer token for a specific product.

        Args:
            subscription_key (str): The subscription key provided by MTN MoMo.
            product (str): The product for which to obtain the token (e.g., 'disbursement', 'remittance').

        Returns:
            str: The Bearer token.

        Raises:
            ValueError: If the product is invalid.
        """
        user = cls.create_api_user(subscription_key)
        api_key = cls.generate_api_key(user['referenceId'], subscription_key)
        token_data = cls.generate_token(user['referenceId'], api_key['apiKey'], product, subscription_key)
        return token_data['access_token']

    @staticmethod
    def validate_token(token):
        """
        Validate the token expiration and regenerate if necessary.

        Args:
            token (str): The Bearer token.

        Returns:
            bool: True if the token is valid, False if it needs to be regenerated.
        """
        # Implement token validation logic here
        # For now, just return True as a placeholder
        return True

    @classmethod
    def get_valid_token(cls, subscription_key, product):
        """
        Get a valid Bearer token, regenerating if necessary.

        Args:
            subscription_key (str): The subscription key provided by MTN MoMo.
            product (str): The product for which to obtain the token (e.g., 'disbursement', 'remittance').

        Returns:
            str: A valid Bearer token.
        """
        token = cls.get_token(subscription_key, product)
        if not cls.validate_token(token):
            token = cls.get_token(subscription_key, product)
        return token


