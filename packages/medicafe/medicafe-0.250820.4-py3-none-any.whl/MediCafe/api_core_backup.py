# MediCafe/api_core.py
"""
Core API functionality for MediCafe.
Moved from MediLink to centralize shared API operations.

COMPATIBILITY: Python 3.4.4 and Windows XP compatible
"""

import time
import json
import os
import traceback

try:
    import yaml
except ImportError:
    yaml = None

try:
    import requests
except ImportError:
    requests = None

# Use core utilities for standardized imports
from MediCafe.core_utils import get_shared_config_loader
MediLink_ConfigLoader = get_shared_config_loader()

"""
Core API client classes and utilities for MediCafe.
This module provides the foundation for all API operations across the project.
"""

class ConfigLoader:
    @staticmethod
    def load_configuration(config_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'config.json'), 
                           crosswalk_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'crosswalk.json')):
        return MediLink_ConfigLoader.load_configuration(config_path, crosswalk_path)

    @staticmethod
    def load_swagger_file(swagger_path):
        try:
            print("Attempting to load Swagger file: {}".format(swagger_path))
            with open(swagger_path, 'r') as swagger_file:
                if swagger_path.endswith('.yaml') or swagger_path.endswith('.yml'):
                    print("Parsing YAML file: {}".format(swagger_path))
                    swagger_data = yaml.safe_load(swagger_file)
                elif swagger_path.endswith('.json'):
                    print("Parsing JSON file: {}".format(swagger_path))
                    swagger_data = json.load(swagger_file)
                else:
                    raise ValueError("Unsupported Swagger file format.")
            print("Successfully loaded Swagger file: {}".format(swagger_path))
            return swagger_data
        except ValueError as e:
            print("Error parsing Swagger file {}: {}".format(swagger_path, e))
            MediLink_ConfigLoader.log("Error parsing Swagger file {}: {}".format(swagger_path, e), level="ERROR")
        except FileNotFoundError:
            print("Swagger file not found: {}".format(swagger_path))
            MediLink_ConfigLoader.log("Swagger file not found: {}".format(swagger_path), level="ERROR")
        except Exception as e:
            print("Unexpected error loading Swagger file {}: {}".format(swagger_path, e))
            MediLink_ConfigLoader.log("Unexpected error loading Swagger file {}: {}".format(swagger_path, e), level="ERROR")
        return None

# Function to ensure numeric type
def ensure_numeric(value):
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            raise ValueError("Cannot convert {} to a numeric type".format(value))
    return value

class TokenCache:
    def __init__(self):
        self.tokens = {}

    def get(self, endpoint_name, current_time):
        token_info = self.tokens.get(endpoint_name, {})
        if token_info:
            expires_at = token_info['expires_at']
            # Log cache hit and expiration time
            log_message = "Token for {} expires at {}. Current time: {}".format(endpoint_name, expires_at, current_time)
            MediLink_ConfigLoader.log(log_message, level="DEBUG")

            if expires_at > current_time:
                return token_info['access_token']

        # Log cache miss
        # Token refresh flow validation has been implemented in get_access_token() to prevent unnecessary token pickup
        log_message = "No valid token found for {}".format(endpoint_name)
        MediLink_ConfigLoader.log(log_message, level="INFO")

        return None

    def set(self, endpoint_name, access_token, expires_in, current_time):
        current_time = ensure_numeric(current_time)
        expires_in = ensure_numeric(expires_in)

        # Log the expires_in value to debug
        log_message = "Token expires in: {} seconds for {}".format(expires_in, endpoint_name)
        MediLink_ConfigLoader.log(log_message, level="INFO")

        # Adjust expiration time by subtracting a buffer of 120 seconds
        buffer_seconds = 120
        adjusted_expires_in = expires_in - buffer_seconds
        
        if adjusted_expires_in <= 0:
            MediLink_ConfigLoader.log("Warning: Token expiration time too short after buffer adjustment", level="WARNING")
            adjusted_expires_in = 60  # Minimum 60 seconds
        
        expires_at = current_time + adjusted_expires_in
        
        self.tokens[endpoint_name] = {
            'access_token': access_token,
            'expires_at': expires_at,
            'expires_in': expires_in
        }
        
        log_message = "Token cached for {} with expiration at {}".format(endpoint_name, expires_at)
        MediLink_ConfigLoader.log(log_message, level="INFO")

class BaseAPIClient:
    def __init__(self, config):
        self.config = config
        self.token_cache = TokenCache()

    def get_access_token(self, endpoint_name):
        raise NotImplementedError("Subclasses should implement this!")

    def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        raise NotImplementedError("Subclasses should implement this!")

class APIClient(BaseAPIClient):
    def __init__(self):
        config, _ = MediLink_ConfigLoader.load_configuration()
        super().__init__(config)
        
        # Add enhanced features if available
        try:
            from MediCafe.api_utils import APICircuitBreaker, APICache, APIRateLimiter
            from MediLink import MediLink_insurance_utils
            get_feature_flag = MediLink_insurance_utils.get_feature_flag
            
            # Initialize enhancements if enabled
            enable_circuit_breaker = get_feature_flag('api_circuit_breaker', default=False)
            enable_caching = get_feature_flag('api_caching', default=False)
            enable_rate_limiting = get_feature_flag('api_rate_limiting', default=False)
            
            self.circuit_breaker = APICircuitBreaker() if enable_circuit_breaker else None
            self.api_cache = APICache() if enable_caching else None
            self.rate_limiter = APIRateLimiter() if enable_rate_limiting else None
            
            if any([enable_circuit_breaker, enable_caching, enable_rate_limiting]):
                MediLink_ConfigLoader.log("Enhanced API client initialized with circuit_breaker={}, caching={}, rate_limiting={}".format(
                    enable_circuit_breaker, enable_caching, enable_rate_limiting), level="INFO")
        except ImportError:
            MediLink_ConfigLoader.log("API enhancements not available, using standard client", level="DEBUG")
            self.circuit_breaker = None
            self.api_cache = None
            self.rate_limiter = None

    def get_access_token(self, endpoint_name):
        MediLink_ConfigLoader.log("[Get Access Token] Called for {}".format(endpoint_name), level="DEBUG")
        current_time = time.time()
        cached_token = self.token_cache.get(endpoint_name, current_time)
        
        if cached_token:
            expires_at = self.token_cache.tokens[endpoint_name]['expires_at']
            MediLink_ConfigLoader.log("Cached token expires at {}".format(expires_at), level="DEBUG")
            return cached_token
        
        # Validate that we actually need a token before fetching
        # Check if the endpoint configuration exists and is valid
        try:
            endpoint_config = self.config['MediLink_Config']['endpoints'][endpoint_name]
            if not endpoint_config:
                MediLink_ConfigLoader.log("No configuration found for endpoint: {}".format(endpoint_name), level="ERROR")
                return None
                
            # Validate required configuration fields
            required_fields = ['token_url', 'client_id', 'client_secret']
            missing_fields = [field for field in required_fields if field not in endpoint_config]
            if missing_fields:
                MediLink_ConfigLoader.log("Missing required configuration fields for {}: {}".format(endpoint_name, missing_fields), level="ERROR")
                return None
                
        except KeyError:
            MediLink_ConfigLoader.log("Endpoint {} not found in configuration".format(endpoint_name), level="ERROR")
            return None
        except Exception as e:
            MediLink_ConfigLoader.log("Error validating endpoint configuration for {}: {}".format(endpoint_name, str(e)), level="ERROR")
            return None
        
        # If no valid token, fetch a new one
        token_url = endpoint_config['token_url']
        data = {
            'grant_type': 'client_credentials',
            'client_id': endpoint_config['client_id'],
            'client_secret': endpoint_config['client_secret']
        }

        # Add scope if specified in the configuration
        if 'scope' in endpoint_config:
            data['scope'] = endpoint_config['scope']

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)

            self.token_cache.set(endpoint_name, access_token, expires_in, current_time)
            MediLink_ConfigLoader.log("Obtained NEW token for endpoint: {}".format(endpoint_name), level="INFO")
            return access_token
        except requests.exceptions.RequestException as e:
            MediLink_ConfigLoader.log("Failed to obtain token for {}: {}".format(endpoint_name, str(e)), level="ERROR")
            return None
        except (KeyError, ValueError) as e:
            MediLink_ConfigLoader.log("Invalid token response for {}: {}".format(endpoint_name, str(e)), level="ERROR")
            return None

    def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        # Try enhanced API call if available
        if hasattr(self, '_make_enhanced_api_call'):
            try:
                return self._make_enhanced_api_call(endpoint_name, call_type, url_extension, params, data, headers)
            except Exception as e:
                MediLink_ConfigLoader.log("Enhanced API call failed, falling back to standard: {}".format(str(e)), level="WARNING")
        
        # Fall back to standard API call
        return self._make_standard_api_call(endpoint_name, call_type, url_extension, params, data, headers)

    def _make_enhanced_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        """Enhanced API call with circuit breaker, caching, and rate limiting."""
        if self.circuit_breaker:
            return self.circuit_breaker.call(self._make_standard_api_call, endpoint_name, call_type, url_extension, params, data, headers)
        else:
            return self._make_standard_api_call(endpoint_name, call_type, url_extension, params, data, headers)

    def _make_standard_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        """Standard API call implementation."""
        try:
            # Get access token
            access_token = self.get_access_token(endpoint_name)
            if not access_token:
                raise Exception("Failed to obtain access token for endpoint: {}".format(endpoint_name))

            # Get endpoint configuration
            endpoint_config = self.config['MediLink_Config']['endpoints'][endpoint_name]
            base_url = endpoint_config['base_url']
            api_url = base_url + url_extension

            # Prepare headers
            if headers is None:
                headers = {}
            
            headers.update({
                'Authorization': 'Bearer {}'.format(access_token),
                'Content-Type': 'application/json'
            })

            # Make the request
            def make_request():
                if call_type.upper() == 'GET':
                    response = requests.get(api_url, headers=headers, params=params)
                elif call_type.upper() == 'POST':
                    response = requests.post(api_url, headers=headers, params=params, json=data)
                elif call_type.upper() == 'PUT':
                    response = requests.put(api_url, headers=headers, params=params, json=data)
                elif call_type.upper() == 'DELETE':
                    response = requests.delete(api_url, headers=headers, params=params)
                else:
                    raise ValueError("Unsupported HTTP method: {}".format(call_type))
                
                response.raise_for_status()
                return response.json()
            
            # Apply rate limiting if available
            if self.rate_limiter:
                return self.rate_limiter.call(make_request)
            else:
                return make_request()

        except Exception as e:
            MediLink_ConfigLoader.log("API call failed for {}: {}".format(endpoint_name, str(e)), level="ERROR")
            raise

# Core API utility functions
def fetch_payer_name_from_api(client, payer_id, config, primary_endpoint='AVAILITY'):
    """
    Fetch payer name from API using the provided client.
    
    Args:
        client: API client instance
        payer_id: Payer ID to look up
        config: Configuration dictionary
        primary_endpoint: Primary endpoint to use for lookup
        
    Returns:
        str: Payer name if found, None otherwise
    """
    try:
        # Try primary endpoint first
        response = client.make_api_call(
            primary_endpoint,
            'GET',
            '/payers/{}'.format(payer_id)
        )
        
        if response and 'name' in response:
            return response['name']
        
        # Try alternative endpoints if primary fails
        alternative_endpoints = ['ELIGIBILITY', 'CLAIMS']
        for endpoint in alternative_endpoints:
            try:
                response = client.make_api_call(
                    endpoint,
                    'GET',
                    '/payers/{}'.format(payer_id)
                )
                
                if response and 'name' in response:
                    return response['name']
            except Exception as e:
                MediLink_ConfigLoader.log("Failed to fetch payer name from {}: {}".format(endpoint, str(e)), level="DEBUG")
                continue
        
        return None
        
    except Exception as e:
        MediLink_ConfigLoader.log("Failed to fetch payer name for {}: {}".format(payer_id, str(e)), level="ERROR")
        return None

def get_eligibility_v3(client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi, 
                       first_name=None, last_name=None, payer_label=None, payer_name=None, service_start=None, service_end=None, 
                       middle_name=None, gender=None, ssn=None, city=None, state=None, zip=None, group_number=None, 
                       service_type_code=None, provider_first_name=None, tax_id_number=None, provider_name_id=None, 
                       corporate_tax_owner_id=None, corporate_tax_owner_name=None, organization_name=None, 
                       organization_id=None, identify_service_level_deductible=True):
    """
    Get eligibility information using v3 API.
    
    Args:
        client: API client instance
        payer_id: Payer ID
        provider_last_name: Provider's last name
        search_option: Search option
        date_of_birth: Date of birth
        member_id: Member ID
        npi: National Provider Identifier
        **kwargs: Additional optional parameters
        
    Returns:
        dict: Eligibility response data
    """
    # Ensure all required parameters have values
    required_params = {
        'payer_id': payer_id,
        'provider_last_name': provider_last_name,
        'search_option': search_option,
        'date_of_birth': date_of_birth,
        'member_id': member_id,
        'npi': npi
    }
    
    # Validate required parameters
    for param_name, param_value in required_params.items():
        if not param_value:
            raise ValueError("Required parameter '{}' is missing or empty".format(param_name))
    
    # Build request data
    request_data = {
        'payer_id': payer_id,
        'provider_last_name': provider_last_name,
        'search_option': search_option,
        'date_of_birth': date_of_birth,
        'member_id': member_id,
        'npi': npi,
        'identify_service_level_deductible': identify_service_level_deductible
    }
    
    # Add optional parameters if provided
    optional_params = {
        'first_name': first_name,
        'last_name': last_name,
        'payer_label': payer_label,
        'payer_name': payer_name,
        'service_start': service_start,
        'service_end': service_end,
        'middle_name': middle_name,
        'gender': gender,
        'ssn': ssn,
        'city': city,
        'state': state,
        'zip': zip,
        'group_number': group_number,
        'service_type_code': service_type_code,
        'provider_first_name': provider_first_name,
        'tax_id_number': tax_id_number,
        'provider_name_id': provider_name_id,
        'corporate_tax_owner_id': corporate_tax_owner_id,
        'corporate_tax_owner_name': corporate_tax_owner_name,
        'organization_name': organization_name,
        'organization_id': organization_id
    }
    
    for param_name, param_value in optional_params.items():
        if param_value is not None:
            request_data[param_name] = param_value
    
    try:
        response = client.make_api_call(
            'ELIGIBILITY',
            'POST',
            '/eligibility/v3',
            data=request_data
        )
        
        return response
        
    except Exception as e:
        MediLink_ConfigLoader.log("Eligibility v3 request failed: {}".format(str(e)), level="ERROR")
        raise 