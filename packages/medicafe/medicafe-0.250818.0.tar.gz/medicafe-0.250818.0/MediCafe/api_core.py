# MediCafe/api_core.py
"""
Core API functionality for MediCafe.
Moved from MediLink to centralize shared API operations.

COMPATIBILITY: Python 3.4.4 and Windows XP compatible
"""

import time, json, os, traceback, sys, requests

# Import centralized logging configuration
try:
    from MediCafe.logging_config import DEBUG, CONSOLE_LOGGING
except ImportError:
    # Fallback to local flags if centralized config is not available
    DEBUG = False
    CONSOLE_LOGGING = False

# Set up project paths first
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

try:
    import yaml
except ImportError:
    yaml = None
try:
    import requests
except ImportError:
    requests = None

# Use core utilities for standardized imports
try:
    from MediCafe.core_utils import get_shared_config_loader
    MediLink_ConfigLoader = get_shared_config_loader()
except ImportError:
    try:
        from .core_utils import get_shared_config_loader
        MediLink_ConfigLoader = get_shared_config_loader()
    except ImportError:
        # Fallback to direct import
        from MediCafe.MediLink_ConfigLoader import MediLink_ConfigLoader

try:
    from MediCafe import graphql_utils as MediLink_GraphQL
except ImportError:
    try:
        from MediLink import MediLink_GraphQL
    except ImportError:
        try:
            import graphql_utils as MediLink_GraphQL
        except ImportError:
            # Create a dummy module if graphql_utils is not available
            class DummyGraphQL:
                @staticmethod
                def transform_eligibility_response(response):
                    return response
            MediLink_GraphQL = DummyGraphQL()

"""
TODO At some point it might make sense to test their acknoledgment endpoint. body is transactionId.
This API is used to extract the claim acknowledgement details for the given transactionid which was 
generated for 837 requests in claim submission process. Claims Acknowledgement (277CA) will provide 
a status of claim-level acknowledgement of all claims received in the front-end processing system and 
adjudication system.
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
                    if yaml is None:
                        print("YAML parsing not available (PyYAML not installed). Please install PyYAML or provide a JSON Swagger file.")
                        return None
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

# Import utilities from api_utils
try:
    from MediCafe.api_utils import TokenCache
except ImportError:
    # Fallback if api_utils is not available
    class TokenCache:
        def __init__(self):
            self.tokens = {}
        def get(self, endpoint_name, current_time):
            return None
        def set(self, endpoint_name, access_token, expires_in, current_time):
            pass

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
        # XP/Python34 Compatibility: Enhanced error handling with verbose output
        try:
            from MediCafe.api_utils import APICircuitBreaker, APICache, APIRateLimiter
            MediLink_ConfigLoader.log("Successfully imported MediCafe.api_utils", level="DEBUG")
        except ImportError as e:
            MediLink_ConfigLoader.log("Warning: MediCafe.api_utils not available: {}".format(str(e)), level="WARNING")
            print("Warning: MediCafe.api_utils import failed: {}".format(str(e)))
            APICircuitBreaker = None
            APICache = None
            APIRateLimiter = None
        except Exception as e:
            MediLink_ConfigLoader.log("Unexpected error importing MediCafe.api_utils: {}".format(str(e)), level="ERROR")
            print("Error: Unexpected MediCafe.api_utils import error: {}".format(str(e)))
            APICircuitBreaker = None
            APICache = None
            APIRateLimiter = None
        
        try:
            try:
                from MediLink import MediLink_insurance_utils
            except Exception:
                MediLink_insurance_utils = None
            if MediLink_insurance_utils is None:
                import importlib
                MediLink_insurance_utils = importlib.import_module('MediLink.MediLink_insurance_utils')
            get_feature_flag = MediLink_insurance_utils.get_feature_flag
            MediLink_ConfigLoader.log("Successfully imported MediLink.MediLink_insurance_utils", level="DEBUG")
        except ImportError as e:
            MediLink_ConfigLoader.log("Warning: MediLink.MediLink_insurance_utils not available: {}".format(str(e)), level="WARNING")
            print("Warning: MediLink.MediLink_insurance_utils import failed: {}".format(str(e)))
            # Provide fallback function
            def get_feature_flag(flag_name, default=False):
                MediLink_ConfigLoader.log("Using fallback get_feature_flag for '{}', returning default: {}".format(flag_name, default), level="DEBUG")
                return default
        except Exception as e:
            MediLink_ConfigLoader.log("Unexpected error importing MediLink.MediLink_insurance_utils: {}".format(str(e)), level="ERROR")
            print("Error: Unexpected MediLink.MediLink_insurance_utils import error: {}".format(str(e)))
            # Provide fallback function
            def get_feature_flag(flag_name, default=False):
                MediLink_ConfigLoader.log("Using fallback get_feature_flag for '{}', returning default: {}".format(flag_name, default), level="DEBUG")
                return default
        
        # Initialize enhancements with error handling
        try:
            enable_circuit_breaker = get_feature_flag('api_circuit_breaker', default=False)
            enable_caching = get_feature_flag('api_caching', default=False)
            enable_rate_limiting = get_feature_flag('api_rate_limiting', default=False)
            
            self.circuit_breaker = APICircuitBreaker() if (enable_circuit_breaker and APICircuitBreaker) else None
            self.api_cache = APICache() if (enable_caching and APICache) else None
            self.rate_limiter = APIRateLimiter() if (enable_rate_limiting and APIRateLimiter) else None
            
            if any([enable_circuit_breaker, enable_caching, enable_rate_limiting]):
                MediLink_ConfigLoader.log("Enhanced API client initialized with circuit_breaker={}, caching={}, rate_limiting={}".format(
                    enable_circuit_breaker, enable_caching, enable_rate_limiting), level="INFO")
            else:
                MediLink_ConfigLoader.log("API enhancements disabled or not available, using standard client", level="DEBUG")
        except Exception as e:
            MediLink_ConfigLoader.log("Error initializing API enhancements: {}. Using standard client.".format(str(e)), level="WARNING")
            print("Warning: API enhancement initialization failed: {}".format(str(e)))
            self.circuit_breaker = None
            self.api_cache = None
            self.rate_limiter = None

    def detect_environment(self, endpoint_name='UHCAPI'):
        """Detect if we're running in staging/test environment for a specific endpoint"""
        try:
            # Look for api_url in the specified endpoint configuration
            from MediCafe.core_utils import extract_medilink_config
            medi = extract_medilink_config(self.config)
            api_url = medi.get('endpoints', {}).get(endpoint_name, {}).get('api_url', '')
            MediLink_ConfigLoader.log("DEBUG: Found API URL for {}: {}".format(endpoint_name, api_url), level="DEBUG")
            
            if 'stg' in api_url.lower() or 'stage' in api_url.lower() or 'test' in api_url.lower():
                MediLink_ConfigLoader.log("DEBUG: Detected staging environment for {} from URL: {}".format(endpoint_name, api_url), level="DEBUG")
                return 'sandbox'
            else:
                MediLink_ConfigLoader.log("DEBUG: No staging indicators found in {} URL: {}".format(endpoint_name, api_url), level="DEBUG")
        except Exception as e:
            MediLink_ConfigLoader.log("DEBUG: Error in environment detection for {}: {}".format(endpoint_name, e), level="DEBUG")
        
        # Default to production (no env parameter)
        return None

    def add_environment_headers(self, headers, endpoint_name):
        """Add environment-specific headers based on detected environment"""
        # TODO: ENVIRONMENT DETECTION ARCHITECTURE ISSUE
        # 
        # Design proposal:
        # - Make env handling strictly per-endpoint and opt-in via config:
        #   config['MediLink_Config']['endpoints'][ep]['use_env_header'] = true|false
        #   config['MediLink_Config']['endpoints'][ep]['env_header_name'] = 'env' (overrideable per endpoint)
        #   config['MediLink_Config']['endpoints'][ep]['staging_indicators'] = ['stg', 'stage', 'test']
        # - If not configured, do NOT inject headers for that endpoint.
        # - Keep current UHC behavior as a fallback to preserve existing behavior.
        # - XP note: keep logic lightweight; avoid heavy regex on each call.
        # 
        # Current Implementation (compat mode):
        if endpoint_name == 'UHCAPI':
            environment = self.detect_environment(endpoint_name)
            if environment:
                headers['env'] = environment
                MediLink_ConfigLoader.log("Added env parameter for staging environment: {}".format(environment), level="INFO", console_output=CONSOLE_LOGGING)
            else:
                MediLink_ConfigLoader.log("No env parameter - using production environment", level="INFO", console_output=CONSOLE_LOGGING)
        return headers

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
            from MediCafe.core_utils import extract_medilink_config
            medi = extract_medilink_config(self.config)
            endpoint_config = medi.get('endpoints', {}).get(endpoint_name)
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
            MediLink_ConfigLoader.log("Obtained NEW token for endpoint: {}".format(endpoint_name), level="INFO", console_output=CONSOLE_LOGGING)
            return access_token
        except requests.exceptions.RequestException as e:
            MediLink_ConfigLoader.log("Failed to obtain token for {}: {}".format(endpoint_name, str(e)), level="ERROR")
            return None
        except (KeyError, ValueError) as e:
            MediLink_ConfigLoader.log("Invalid token response for {}: {}".format(endpoint_name, str(e)), level="ERROR")
            return None

    def make_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        # Try enhanced API call if available
        if hasattr(self, 'circuit_breaker') and self.circuit_breaker:
            try:
                return self._make_enhanced_api_call(endpoint_name, call_type, url_extension, params, data, headers)
            except Exception as e:
                MediLink_ConfigLoader.log("Enhanced API call failed, falling back to standard: {}".format(str(e)), level="WARNING")
        
        # Standard API call logic
        return self._make_standard_api_call(endpoint_name, call_type, url_extension, params, data, headers)
    
    def _make_enhanced_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        """Enhanced API call with circuit breaker, caching, and rate limiting"""
        # Check cache first (for GET requests)
        if self.api_cache and call_type == 'GET':
            cached_result = self.api_cache.get(endpoint_name, call_type, url_extension, params)
            if cached_result is not None:
                MediLink_ConfigLoader.log("Cache hit for {} {} {}".format(call_type, endpoint_name, url_extension), level="DEBUG")
                return cached_result
        
        # Check rate limits
        if self.rate_limiter:
            self.rate_limiter.wait_if_needed()
        
        # Make call with circuit breaker protection
        result = self.circuit_breaker.call_with_breaker(
            self._make_standard_api_call, endpoint_name, call_type, url_extension, params, data, headers)
        
        # Record rate limit call
        if self.rate_limiter:
            self.rate_limiter.record_call()
        
        # Cache result (for GET requests)
        if self.api_cache and call_type == 'GET':
            self.api_cache.set(result, endpoint_name, call_type, url_extension, params)
        
        return result
    
    def _make_standard_api_call(self, endpoint_name, call_type, url_extension="", params=None, data=None, headers=None):
        """Standard API call logic preserved for compatibility"""
        token = self.get_access_token(endpoint_name)
        if token:
            MediLink_ConfigLoader.log("[Make API Call] Token found for {}".format(endpoint_name), level="DEBUG")
        else:
            MediLink_ConfigLoader.log("[Make API Call] No token obtained for {}".format(endpoint_name), level="ERROR")
            raise ValueError("No access token available for endpoint: {}".format(endpoint_name))

        if headers is None:
            headers = {}
        headers.update({'Authorization': 'Bearer {}'.format(token), 'Accept': 'application/json'})
        
        # Add environment-specific headers automatically
        headers = self.add_environment_headers(headers, endpoint_name)
        
        from MediCafe.core_utils import extract_medilink_config
        medi = extract_medilink_config(self.config)
        base_url = medi.get('endpoints', {}).get(endpoint_name, {}).get('api_url', '')
        if not base_url:
            raise ValueError("Missing api_url for endpoint {}".format(endpoint_name))
        url = base_url + url_extension

        # VERBOSE LOGGING: Log all request details before making the call
        if DEBUG:
            MediLink_ConfigLoader.log("=" * 80, level="INFO")
            MediLink_ConfigLoader.log("VERBOSE API CALL DETAILS", level="INFO")
            MediLink_ConfigLoader.log("=" * 80, level="INFO")
            MediLink_ConfigLoader.log("Endpoint Name: {}".format(endpoint_name), level="INFO")
            MediLink_ConfigLoader.log("Call Type: {}".format(call_type), level="INFO")
            MediLink_ConfigLoader.log("Base URL: {}".format(base_url), level="INFO")
            MediLink_ConfigLoader.log("URL Extension: {}".format(url_extension), level="INFO")
            MediLink_ConfigLoader.log("Full URL: {}".format(url), level="INFO")
            MediLink_ConfigLoader.log("Headers: {}".format(json.dumps(headers, indent=2)), level="INFO")
            if params:
                MediLink_ConfigLoader.log("Query Parameters: {}".format(json.dumps(params, indent=2)), level="INFO")
            else:
                MediLink_ConfigLoader.log("Query Parameters: None", level="INFO")
            if data:
                MediLink_ConfigLoader.log("Request Data: {}".format(json.dumps(data, indent=2)), level="INFO")
            else:
                MediLink_ConfigLoader.log("Request Data: None", level="INFO")
            MediLink_ConfigLoader.log("=" * 80, level="INFO")

        try:
            masked_headers = headers.copy()
            if 'Authorization' in masked_headers:
                masked_headers['Authorization'] = 'Bearer ***'

            def make_request():
                if call_type == 'GET':
                    if DEBUG:
                        MediLink_ConfigLoader.log("Making GET request to: {}".format(url), level="INFO")
                    return requests.get(url, headers=headers, params=params)
                elif call_type == 'POST':
                    # Check if there are custom headers (any headers beyond Authorization and Accept)
                    custom_headers = {k: v for k, v in headers.items() if k not in ['Authorization', 'Accept']}
                    
                    if custom_headers:
                        # Log that custom headers were detected
                        MediLink_ConfigLoader.log("Custom headers detected: {}".format(custom_headers), level="DEBUG")
                    else:
                        # Set default Content-Type if no custom headers
                        headers['Content-Type'] = 'application/json'
                    
                    if DEBUG:
                        MediLink_ConfigLoader.log("Making POST request to: {}".format(url), level="INFO")
                    return requests.post(url, headers=headers, json=data)
                elif call_type == 'DELETE':
                    if DEBUG:
                        MediLink_ConfigLoader.log("Making DELETE request to: {}".format(url), level="INFO")
                    return requests.delete(url, headers=headers)
                else:
                    raise ValueError("Unsupported call type: {}".format(call_type))

            # Make initial request
            response = make_request()

            # VERBOSE LOGGING: Log response details
            if DEBUG:
                MediLink_ConfigLoader.log("=" * 80, level="INFO")
                MediLink_ConfigLoader.log("VERBOSE RESPONSE DETAILS", level="INFO")
                MediLink_ConfigLoader.log("=" * 80, level="INFO")
                MediLink_ConfigLoader.log("Response Status Code: {}".format(response.status_code), level="INFO")
                MediLink_ConfigLoader.log("Response Headers: {}".format(json.dumps(dict(response.headers), indent=2)), level="INFO")
                
                try:
                    response_json = response.json()
                    MediLink_ConfigLoader.log("Response JSON: {}".format(json.dumps(response_json, indent=2)), level="INFO")
                except ValueError:
                    MediLink_ConfigLoader.log("Response Text (not JSON): {}".format(response.text), level="INFO")
                
                MediLink_ConfigLoader.log("=" * 80, level="INFO")

            # If we get a 5xx error, wait and retry once
            if 500 <= response.status_code < 600:
                error_msg = "Received {} error from server for {} request to {}. Waiting 1 second before retry...".format(
                    response.status_code, call_type, url
                )
                MediLink_ConfigLoader.log(error_msg, level="WARNING")
                
                # Add more verbose logging for 504 errors specifically
                if response.status_code == 504:
                    MediLink_ConfigLoader.log(
                        "504 Gateway Timeout detected. This usually indicates the server is overloaded or taking too long to respond. "
                        "Retrying after 1 second delay...", 
                        level="WARNING"
                    )
                
                time.sleep(1)
                response = make_request()
                
                # Log the retry result
                if response.status_code == 200:
                    MediLink_ConfigLoader.log(
                        "Retry successful! Request to {} now returned 200 status code.".format(url),
                        level="INFO"
                    )
                else:
                    MediLink_ConfigLoader.log(
                        "Retry failed. Request to {} still returned {} status code.".format(url, response.status_code),
                        level="ERROR"
                    )

            # Raise an HTTPError if the response was unsuccessful
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            # VERBOSE ERROR LOGGING
            MediLink_ConfigLoader.log("=" * 80, level="ERROR")
            MediLink_ConfigLoader.log("VERBOSE HTTP ERROR DETAILS", level="ERROR")
            MediLink_ConfigLoader.log("=" * 80, level="ERROR")
            
            # If http_err.response is None, handle it separately
            if http_err.response is None:
                log_message = (
                    "HTTPError with no response. "
                    "URL: {url}, "
                    "Method: {method}, "
                    "Params: {params}, "
                    "Data: {data}, "
                    "Headers: {masked_headers}, "
                    "Error: {error}"
                ).format(
                    url=url,
                    method=call_type,
                    params=params,
                    data=data,
                    masked_headers=masked_headers,
                    error=str(http_err)
                )
                MediLink_ConfigLoader.log(log_message, level="ERROR")
            else:
                # Extract status code and full response content
                status_code = http_err.response.status_code
                MediLink_ConfigLoader.log("HTTP Error Status Code: {}".format(status_code), level="ERROR")
                MediLink_ConfigLoader.log("HTTP Error URL: {}".format(url), level="ERROR")
                MediLink_ConfigLoader.log("HTTP Error Method: {}".format(call_type), level="ERROR")
                MediLink_ConfigLoader.log("HTTP Error Headers: {}".format(json.dumps(masked_headers, indent=2)), level="ERROR")
                
                if params:
                    MediLink_ConfigLoader.log("HTTP Error Query Params: {}".format(json.dumps(params, indent=2)), level="ERROR")
                if data:
                    MediLink_ConfigLoader.log("HTTP Error Request Data: {}".format(json.dumps(data, indent=2)), level="ERROR")
                
                try:
                    # Try to log the JSON content if available
                    response_content = http_err.response.json()
                    MediLink_ConfigLoader.log("HTTP Error Response JSON: {}".format(json.dumps(response_content, indent=2)), level="ERROR")
                except ValueError:
                    # Fallback to raw text if JSON decoding fails
                    response_content = http_err.response.text
                    MediLink_ConfigLoader.log("HTTP Error Response Text: {}".format(response_content), level="ERROR")

                log_message = (
                    "HTTPError: Status Code: {status}, "
                    "URL: {url}, "
                    "Method: {method}, "
                    "Params: {params}, "
                    "Data: {data}, "
                    "Headers: {masked_headers}, "
                    "Response Content: {content}"
                ).format(
                    status=status_code,
                    url=url,
                    method=call_type,
                    params=params,
                    data=data,
                    masked_headers=masked_headers,
                    content=response_content
                )
                MediLink_ConfigLoader.log(log_message, level="ERROR")
            
            MediLink_ConfigLoader.log("=" * 80, level="ERROR")
            raise

        except requests.exceptions.RequestException as req_err:
            # Log connection-related issues or other request exceptions
            log_message = (
                "RequestException: No response received. "
                "URL: {url}, "
                "Method: {method}, "
                "Params: {params}, "
                "Data: {data}, "
                "Headers: {masked_headers}, "
                "Error: {error}"
            ).format(
                url=url,
                method=call_type,
                params=params,
                data=data,
                masked_headers=masked_headers,
                error=str(req_err)
            )
            MediLink_ConfigLoader.log(log_message, level="ERROR")
            raise

        except Exception as e:
            # Capture traceback for unexpected exceptions
            tb = traceback.format_exc()
            log_message = (
                "Unexpected error: {error}. "
                "URL: {url}, "
                "Method: {method}, "
                "Params: {params}, "
                "Data: {data}, "
                "Headers: {masked_headers}. "
                "Traceback: {traceback}"
            ).format(
                error=str(e),
                url=url,
                method=call_type,
                params=params,
                data=data,
                masked_headers=masked_headers,
                traceback=tb
            )
            MediLink_ConfigLoader.log(log_message, level="ERROR")
            raise

def fetch_payer_name_from_api(client, payer_id, config, primary_endpoint='AVAILITY'):
    """
    Fetches the payer name using the provided APIClient instance.

    :param client: An instance of APIClient
    :param payer_id: The payer ID to fetch
    :param primary_endpoint: The primary endpoint to use
    :return: The payer name if found
    """
    # Ensure client is an instance of APIClient
    if not isinstance(client, APIClient):
        error_message = "Invalid client provided. Expected an instance of APIClient."
        print(error_message)
        MediLink_ConfigLoader.log(error_message, level="ERROR")
        exit(1)  # Exit the script
    
    # TODO: FUTURE IMPLEMENTATION - Remove AVAILITY default when other endpoints have payer-list APIs
    # Currently defaulting to AVAILITY as it's the only endpoint with confirmed payer-list functionality
    # In the future, this should be removed and the system should dynamically detect which endpoints
    # have payer-list capabilities and use them accordingly.
    if primary_endpoint != 'AVAILITY':
        MediLink_ConfigLoader.log("[Fetch payer name from API] Overriding {} with AVAILITY (default until multi-endpoint payer-list support is implemented).".format(primary_endpoint), level="DEBUG")
        primary_endpoint = 'AVAILITY'
    
    try:
        from MediCafe.core_utils import extract_medilink_config
        medi = extract_medilink_config(config)
        endpoints = medi.get('endpoints', {})
    except KeyError as e:
        error_message = "Configuration loading error in fetch_payer_name_from_api: Missing key {0}... Attempting to reload configuration.".format(e)
        # print(error_message)
        MediLink_ConfigLoader.log(error_message, level="ERROR")
        # Attempt to reload configuration if key is missing
        config, _ = MediLink_ConfigLoader.load_configuration()
        # SAFE FALLBACK: if endpoints still missing, fall back to AVAILITY only and proceed.
        from MediCafe.core_utils import extract_medilink_config
        medi = extract_medilink_config(config)
        endpoints = medi.get('endpoints', {})
        if not endpoints:
            MediLink_ConfigLoader.log("Endpoints configuration missing after reload. Falling back to AVAILITY-only logic.", level="WARNING")
        MediLink_ConfigLoader.log("Re-loaded configuration successfully.", level="INFO")
    
    # Sanitize and validate payer_id
    if not isinstance(payer_id, str):
        payer_id = str(payer_id)
    
    payer_id = ''.join(char for char in payer_id if char.isalnum())
    
    if not payer_id:
        error_message = "Invalid payer_id in API v3: {}. Must contain a string of alphanumeric characters.".format(payer_id)
        MediLink_ConfigLoader.log(error_message, level="ERROR")
        print(error_message)
    
    # FUTURE IMPLEMENTATION: Dynamic endpoint selection based on payer-list availability
    # This will replace the hardcoded AVAILITY default when other endpoints have payer-list APIs
    # The logic should:
    # 1. Check all endpoints for 'payer_list_endpoint' configuration
    # 2. Prioritize endpoints that have confirmed payer-list functionality
    # 3. Fall back to endpoints with basic payer lookup if available
    # 4. Use AVAILITY as final fallback
    
    # Define endpoint rotation logic with payer-list capability detection
    available_endpoints = []
    
    # Check which endpoints have payer-list functionality configured
    for endpoint_name, endpoint_config in endpoints.items():
        if 'payer_list_endpoint' in endpoint_config:
            available_endpoints.append(endpoint_name)
            MediLink_ConfigLoader.log("Found payer-list endpoint for {}: {}".format(endpoint_name, endpoint_config['payer_list_endpoint']), level="DEBUG")
    
    # If no endpoints have payer-list configured, fall back to AVAILITY
    if not available_endpoints:
        MediLink_ConfigLoader.log("No endpoints with payer-list configuration found, using AVAILITY as fallback", level="INFO")
        available_endpoints = ['AVAILITY']
    
    # Prioritize the primary endpoint if it has payer-list capability
    if primary_endpoint in available_endpoints:
        endpoint_order = [primary_endpoint] + [ep for ep in available_endpoints if ep != primary_endpoint]
    else:
        # If primary endpoint doesn't have payer-list, use available endpoints in order
        endpoint_order = available_endpoints
    
    MediLink_ConfigLoader.log("Endpoint order for payer lookup: {}".format(endpoint_order), level="DEBUG")

    for endpoint_name in endpoint_order:
        try:
            endpoint_url = endpoints[endpoint_name].get('payer_list_endpoint', '/availity-payer-list')
            response = client.make_api_call(endpoint_name, 'GET', endpoint_url, {'payerId': payer_id})
            
            # Check if response exists
            if not response:
                log_message = "No response from {0} for Payer ID {1}".format(endpoint_name, payer_id)
                print(log_message)
                MediLink_ConfigLoader.log(log_message, level="ERROR")
                continue
            
            # Check if the status code is not 200
            status_code = response.get('statuscode', 200)
            if status_code != 200:
                log_message = "Invalid response status code {0} from {1} for Payer ID {2}. Message: {3}".format(
                    status_code, endpoint_name, payer_id, response.get('message', 'No message'))
                print(log_message)
                MediLink_ConfigLoader.log(log_message, level="ERROR")
                continue
            
            # Extract payers and validate the response structure
            payers = response.get('payers', [])
            if not payers:
                log_message = "No payer found at {0} for ID {1}. Response: {2}".format(endpoint_name, payer_id, response)
                print(log_message)
                MediLink_ConfigLoader.log(log_message, level="INFO")
                continue
            
            # Extract the payer name from the first payer in the list
            payer_name = payers[0].get('displayName') or payers[0].get('name')
            if not payer_name:
                log_message = "Payer name not found in the response from {0} for ID {1}. Response: {2}".format(
                    endpoint_name, payer_id, response)
                print(log_message)
                MediLink_ConfigLoader.log(log_message, level="ERROR")
                continue
            
            # Log successful payer retrieval
            log_message = "Found payer at {0} for ID {1}: {2}".format(endpoint_name, payer_id, payer_name)
            MediLink_ConfigLoader.log(log_message, level="INFO")
            return payer_name
        
        except Exception as e:
            error_message = "Error calling {0} for Payer ID {1}. Exception: {2}".format(endpoint_name, payer_id, e)
            MediLink_ConfigLoader.log(error_message, level="INFO")

    # If all endpoints fail
    final_error_message = "All endpoints exhausted for Payer ID {0}.".format(payer_id)
    print(final_error_message)
    MediLink_ConfigLoader.log(final_error_message, level="CRITICAL")
    raise ValueError(final_error_message)

def get_claim_summary_by_provider(client, tin, first_service_date, last_service_date, payer_id, get_standard_error='false', transaction_id=None, env=None):
    # VERBOSE LOGGING FOR CLAIM SUMMARY
    if DEBUG:
        MediLink_ConfigLoader.log("=" * 80, level="INFO")
        MediLink_ConfigLoader.log("GET CLAIM SUMMARY BY PROVIDER - VERBOSE DETAILS", level="INFO")
        MediLink_ConfigLoader.log("=" * 80, level="INFO")
        MediLink_ConfigLoader.log("TIN: {}".format(tin), level="INFO")
        MediLink_ConfigLoader.log("First Service Date: {}".format(first_service_date), level="INFO")
        MediLink_ConfigLoader.log("Last Service Date: {}".format(last_service_date), level="INFO")
        MediLink_ConfigLoader.log("Payer ID: {}".format(payer_id), level="INFO")
        MediLink_ConfigLoader.log("Get Standard Error: {}".format(get_standard_error), level="INFO")
        MediLink_ConfigLoader.log("Transaction ID: {}".format(transaction_id), level="INFO")
        MediLink_ConfigLoader.log("Environment: {}".format(env), level="INFO")
        MediLink_ConfigLoader.log("=" * 80, level="INFO")
    
    endpoint_name = 'UHCAPI'
    from MediCafe.core_utils import extract_medilink_config
    medi = extract_medilink_config(client.config)
    url_extension = medi.get('endpoints', {}).get(endpoint_name, {}).get('additional_endpoints', {}).get('claim_summary_by_provider', '')
    
    if DEBUG:
        MediLink_ConfigLoader.log("URL Extension: {}".format(url_extension), level="INFO")
    
    # Build headers according to official API documentation
    # Note: Environment detection is now handled automatically by the API client
    headers = {
        'tin': tin,
        'firstServiceDt': first_service_date,
        'lastServiceDt': last_service_date,
        'payerId': payer_id,
        'getStandardError': get_standard_error,
        'Accept': 'application/json'
    }
    
    # Add transactionId if provided (for pagination)
    if transaction_id:
        headers['transactionId'] = transaction_id
    
    if DEBUG:
        MediLink_ConfigLoader.log("Headers: {}".format(json.dumps(headers, indent=2)), level="INFO")
    
    return client.make_api_call(endpoint_name, 'GET', url_extension, params=None, data=None, headers=headers)

def get_eligibility(client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi):
    endpoint_name = 'UHCAPI'
    from MediCafe.core_utils import extract_medilink_config
    medi = extract_medilink_config(client.config)
    url_extension = medi.get('endpoints', {}).get(endpoint_name, {}).get('additional_endpoints', {}).get('eligibility', '')
    url_extension = url_extension + '?payerID={}&providerLastName={}&searchOption={}&dateOfBirth={}&memberId={}&npi={}'.format(
        payer_id, provider_last_name, search_option, date_of_birth, member_id, npi)
    return client.make_api_call(endpoint_name, 'GET', url_extension)

def get_eligibility_v3(client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi, 
                       first_name=None, last_name=None, payer_label=None, payer_name=None, service_start=None, service_end=None, 
                       middle_name=None, gender=None, ssn=None, city=None, state=None, zip=None, group_number=None, 
                       service_type_code=None, provider_first_name=None, tax_id_number=None, provider_name_id=None, 
                       corporate_tax_owner_id=None, corporate_tax_owner_name=None, organization_name=None, 
                       organization_id=None, identify_service_level_deductible=True):

    # Ensure all required parameters have values
    if not all([client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi]):
        raise ValueError("All required parameters must have values: client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi")

    # Validate payer_id
    valid_payer_ids = ["87726", "06111", "25463", "37602", "39026", "74227", "65088", "81400", "03432", "86050", "86047", "95378", "95467"]
    if payer_id not in valid_payer_ids:
        raise ValueError("Invalid payer_id: {}. Must be one of: {}".format(payer_id, ", ".join(valid_payer_ids)))
    
    endpoint_name = 'UHCAPI'
    from MediCafe.core_utils import extract_medilink_config
    medi = extract_medilink_config(client.config)
    url_extension = medi.get('endpoints', {}).get(endpoint_name, {}).get('additional_endpoints', {}).get('eligibility_v3', '')
    
    # Construct request body
    body = {
        "memberId": member_id,
        "lastName": last_name,
        "firstName": first_name,
        "dateOfBirth": date_of_birth,
        "payerID": payer_id,
        "payerLabel": payer_label,
        "payerName": payer_name,
        "serviceStart": service_start,
        "serviceEnd": service_end,
        "middleName": middle_name,
        "gender": gender,
        "ssn": ssn,
        "city": city,
        "state": state,
        "zip": zip,
        "groupNumber": group_number,
        "serviceTypeCode": service_type_code,
        "providerLastName": provider_last_name,
        "providerFirstName": provider_first_name,
        "taxIdNumber": tax_id_number,
        "providerNameID": provider_name_id,
        "npi": npi,
        "corporateTaxOwnerID": corporate_tax_owner_id,
        "corporateTaxOwnerName": corporate_tax_owner_name,
        "organizationName": organization_name,
        "organizationID": organization_id,
        "searchOption": search_option,
        "identifyServiceLevelDeductible": identify_service_level_deductible
    }
    
    # Remove None values from the body
    body = {k: v for k, v in body.items() if v is not None}

    # Log the request body
    MediLink_ConfigLoader.log("Request body: {}".format(json.dumps(body, indent=4)), level="DEBUG")

    return client.make_api_call(endpoint_name, 'POST', url_extension, params=None, data=body)

def get_eligibility_super_connector(client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi, 
                                   first_name=None, last_name=None, payer_label=None, payer_name=None, service_start=None, service_end=None, 
                                   middle_name=None, gender=None, ssn=None, city=None, state=None, zip=None, group_number=None, 
                                   service_type_code=None, provider_first_name=None, tax_id_number=None, provider_name_id=None, 
                                   corporate_tax_owner_id=None, corporate_tax_owner_name=None, organization_name=None, 
                                   organization_id=None, identify_service_level_deductible=True):
    """
    GraphQL Super Connector version of eligibility check that maps to the same interface as get_eligibility_v3.
    This function provides a drop-in replacement for the REST API with identical input/output behavior.
    """
    # Ensure all required parameters have values
    if not all([client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi]):
        raise ValueError("All required parameters must have values: client, payer_id, provider_last_name, search_option, date_of_birth, member_id, npi")

    # Validate payer_id
    valid_payer_ids = ["87726", "06111", "25463", "37602", "39026", "74227", "65088", "81400", "03432", "86050", "86047", "95378", "95467"]
    if payer_id not in valid_payer_ids:
        raise ValueError("Invalid payer_id: {}. Must be one of: {}".format(payer_id, ", ".join(valid_payer_ids)))
    
    endpoint_name = 'UHCAPI'
    url_extension = client.config['MediLink_Config']['endpoints'][endpoint_name]['additional_endpoints']['eligibility_super_connector']
    
    # Get provider TIN from config (using existing billing_provider_tin)
    from MediCafe.core_utils import extract_medilink_config
    medi = extract_medilink_config(client.config)
    provider_tin = medi.get('billing_provider_tin')
    if not provider_tin:
        raise ValueError("Provider TIN not found in configuration")
    
    # Construct GraphQL query variables using the consolidated module
    graphql_variables = MediLink_GraphQL.build_eligibility_variables(
        member_id=member_id,
        date_of_birth=date_of_birth,
        payer_id=payer_id,
        provider_last_name=provider_last_name,
        provider_npi=npi
    )
    
    # Validate NPI format (should be 10 digits)
    if 'providerNPI' in graphql_variables:
        npi_value = graphql_variables['providerNPI']
        if not npi_value.isdigit() or len(npi_value) != 10:
            MediLink_ConfigLoader.log("Warning: NPI '{}' is not 10 digits, but continuing anyway".format(npi_value), level="WARNING")
    
    # Build GraphQL request using the consolidated module
    # Hardcoded switch to use sample data for testing
    USE_SAMPLE_DATA = False  # Set to False to use constructed data
    
    if USE_SAMPLE_DATA:
        # Use the sample data from swagger documentation
        graphql_body = MediLink_GraphQL.get_sample_eligibility_request()
        MediLink_ConfigLoader.log("Using SAMPLE DATA from swagger documentation", level="INFO")
    else:
        # Build GraphQL request with actual data using consolidated module
        graphql_body = MediLink_GraphQL.build_eligibility_request(graphql_variables)
        MediLink_ConfigLoader.log("Using CONSTRUCTED DATA with consolidated GraphQL module", level="INFO")
        
        # Compare with sample data for debugging
        sample_data = MediLink_GraphQL.get_sample_eligibility_request()
        MediLink_ConfigLoader.log("Sample data structure: {}".format(json.dumps(sample_data, indent=2)), level="DEBUG")
        MediLink_ConfigLoader.log("Constructed data structure: {}".format(json.dumps(graphql_body, indent=2)), level="DEBUG")
        
        # Compare key differences
        sample_vars = sample_data['variables']['input']
        constructed_vars = graphql_body['variables']['input']
        
        # Log differences in variables
        for key in set(sample_vars.keys()) | set(constructed_vars.keys()):
            sample_val = sample_vars.get(key)
            constructed_val = constructed_vars.get(key)
            if sample_val != constructed_val:
                MediLink_ConfigLoader.log("Variable difference - {}: sample='{}', constructed='{}'".format(
                    key, sample_val, constructed_val), level="DEBUG")
    
    # Log the GraphQL request
    MediLink_ConfigLoader.log("GraphQL request body: {}".format(json.dumps(graphql_body, indent=2)), level="DEBUG")
    MediLink_ConfigLoader.log("GraphQL variables: {}".format(json.dumps(graphql_variables, indent=2)), level="DEBUG")
    
    # Add required headers for Super Connector
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'tin': str(provider_tin)  # Ensure TIN is a string
    }
    
    # Only add env header when using sample data
    if USE_SAMPLE_DATA:
        headers['env'] = 'sandbox'
    
    # Remove None values from headers
    headers = {k: v for k, v in headers.items() if v is not None}
    
    # Log the final headers being sent
    MediLink_ConfigLoader.log("Final headers being sent: {}".format(json.dumps(headers, indent=2)), level="DEBUG")
    
    # Make the GraphQL API call
    response = client.make_api_call(endpoint_name, 'POST', url_extension, params=None, data=graphql_body, headers=headers)
    
    # Transform GraphQL response to match REST API format
    # This ensures the calling code doesn't know the difference
    transformed_response = MediLink_GraphQL.transform_eligibility_response(response)
    
    return transformed_response

def is_test_mode(client, body, endpoint_type):
    """
    Checks if Test Mode is enabled in the client's configuration and simulates the response if it is.

    :param client: An instance of APIClient
    :param body: The intended request body
    :param endpoint_type: The type of endpoint being accessed ('claim_submission' or 'claim_details')
    :return: A dummy response simulating the real API call if Test Mode is enabled, otherwise None
    """
    if client.config.get("MediLink_Config", {}).get("TestMode", True):
        print("Test Mode is enabled! API Call not executed.")
        print("\nIntended request body:", body)
        MediLink_ConfigLoader.log("Test Mode is enabled! Simulating 1 second delay for API response for {}.".format(endpoint_type), level="INFO")
        time.sleep(1)
        MediLink_ConfigLoader.log("Intended request body: {}".format(body), level="INFO")

        if endpoint_type == 'claim_submission':
            dummy_response = {
                "transactionId": "CS07180420240328013411240",  # This is the tID for the sandbox Claim Acknowledgement endpoint.
                "x12ResponseData": "ISA*00* *00* *ZZ*TEST1234567890 *33*TEST *210101*0101*^*00501*000000001*0*P*:~GS*HC*TEST1234567890*TEST*20210101*0101*1*X*005010X222A1~ST*837*000000001*005010X222A1~BHT*0019*00*00001*20210101*0101*CH~NM1*41*2*TEST SUBMITTER*****46*TEST~PER*IC*TEST CONTACT*TE*1234567890~NM1*40*2*TEST RECEIVER*****46*TEST~HL*1**20*1~NM1*85*2*TEST PROVIDER*****XX*1234567890~N3*TEST ADDRESS~N4*TEST CITY*TEST STATE*12345~REF*EI*123456789~PER*IC*TEST PROVIDER*TE*1234567890~NM1*87*2~N3*TEST ADDRESS~N4*TEST CITY*TEST STATE*12345~HL*2*1*22*0~SBR*P*18*TEST GROUP******CI~NM1*IL*1*TEST PATIENT****MI*123456789~N3*TEST ADDRESS~N4*TEST CITY*TEST STATE*12345~DMG*D8*19800101*M~NM1*PR*2*TEST INSURANCE*****PI*12345~CLM*TESTCLAIM*100***12:B:1*Y*A*Y*Y*P~REF*D9*TESTREFERENCE~HI*ABK:TEST~NM1*DN*1*TEST DOCTOR****XX*1234567890~LX*1~SV1*HC:TEST*100*UN*1***1~DTP*472*RD8*20210101-20210101~REF*6R*TESTREFERENCE~SE*30*000000001~GE*1*1~IEA*1*000000001~",
                "responseType": "dummy_response_837999",
                "message": "Test Mode: Claim validated and sent for further processing"
            }
        elif endpoint_type == 'claim_details':
            dummy_response = {
                "responseType": "dummy_response_277CA-CH",
                "x12ResponseData": "ISA*00* *00*  *ZZ*841162764 *ZZ*UB920086 *240318*0921*^*00501*000165687*0*T*:~GS*HN*841162764*UB920086*20240318*0921*0165687*X*005010X214~ST*277*000000006*005010X214~... SE*116*000000006~GE*1*0165687~IEA*1*000165687~",
                "statuscode": "000",
                "message:": ""
            }
        return dummy_response
    return None

def submit_uhc_claim(client, x12_request_data):
    """
    Submits a UHC claim and retrieves the claim acknowledgement details.
    
    This function first submits the claim using the provided x12 837p data. If the client is in Test Mode, 
    it returns a simulated response. If Test Mode is not enabled, it submits the claim and then retrieves 
    the claim acknowledgement details using the transaction ID from the initial response.
    
    NOTE: This function uses endpoints that may not be available in the new swagger version:
    - /Claims/api/claim-submission/v1 (claim submission)
    - /Claims/api/claim-details/v1 (claim acknowledgement)
    
    If these endpoints are deprecated in the new swagger, this function will need to be updated
    to use the new available endpoints.
    
    :param client: An instance of APIClient
    :param x12_request_data: The x12 837p data as a string
    :return: The final response containing the claim acknowledgement details or a dummy response if in Test Mode
    """
    # VERBOSE LOGGING FOR CLAIM SUBMISSION
    MediLink_ConfigLoader.log("=" * 80, level="INFO")
    MediLink_ConfigLoader.log("SUBMIT UHC CLAIM - VERBOSE DETAILS", level="INFO")
    MediLink_ConfigLoader.log("=" * 80, level="INFO")
    MediLink_ConfigLoader.log("X12 Request Data Length: {}".format(len(x12_request_data) if x12_request_data else 0), level="INFO")
    if x12_request_data:
        MediLink_ConfigLoader.log("X12 Request Data Preview (first 200 chars): {}".format(x12_request_data[:200]), level="INFO")
    MediLink_ConfigLoader.log("=" * 80, level="INFO")
    
    endpoint_name = 'UHCAPI'
    from MediCafe.core_utils import extract_medilink_config
    medi = extract_medilink_config(client.config)
    endpoints = medi.get('endpoints', {})
    claim_submission_url = endpoints.get(endpoint_name, {}).get('additional_endpoints', {}).get('claim_submission', '')
    claim_details_url = endpoints.get(endpoint_name, {}).get('additional_endpoints', {}).get('claim_details', '')
 
    MediLink_ConfigLoader.log("Claim Submission URL: {}".format(claim_submission_url), level="INFO")
    MediLink_ConfigLoader.log("Claim Details URL: {}".format(claim_details_url), level="INFO")
 
    # Headers for the request
    headers = {'Content-Type': 'application/json'} 
 
    # Request body for claim submission
    claim_body = {'x12RequestData': x12_request_data}
 
    MediLink_ConfigLoader.log("Claim Body Keys: {}".format(list(claim_body.keys())), level="INFO")
    MediLink_ConfigLoader.log("Headers: {}".format(json.dumps(headers, indent=2)), level="INFO")
 
    # Check if Test Mode is enabled and return simulated response if so
    test_mode_response = is_test_mode(client, claim_body, 'claim_submission')
    if test_mode_response:
        return test_mode_response
 
    # Make the API call to submit the claim
    try:
        MediLink_ConfigLoader.log("Making claim submission API call...", level="INFO")
        submission_response = client.make_api_call(endpoint_name, 'POST', claim_submission_url, data=claim_body, headers=headers)
        
        # Extract the transaction ID from the submission response
        transaction_id = submission_response.get('transactionId')
        if not transaction_id:
            raise ValueError("transactionId not found in the submission response")
        
        # Log the transaction ID for traceability
        MediLink_ConfigLoader.log("UHCAPI claim submission transactionId: {}".format(transaction_id), level="INFO")
        
        # Prepare the request body for the claim acknowledgement retrieval
        acknowledgement_body = {'transactionId': transaction_id}
 
        # Check if Test Mode is enabled and return simulated response if so
        test_mode_response = is_test_mode(client, acknowledgement_body, 'claim_details')
        if test_mode_response:
            return test_mode_response
 
        # Make the API call to retrieve the claim acknowledgement details
        acknowledgement_response = client.make_api_call(endpoint_name, 'POST', claim_details_url, data=acknowledgement_body, headers=headers)
        
        # Persist as unified ack event (best-effort)
        try:
            from MediCafe.submission_index import append_ack_event, ensure_submission_index
            cfg, _ = MediLink_ConfigLoader.load_configuration()
            receipts_root = extract_medilink_config(cfg).get('local_claims_path', None)
            if receipts_root:
                ensure_submission_index(receipts_root)
                status_text = ''
                try:
                    # Attempt to pull a readable status from the response
                    status_text = acknowledgement_response.get('status') or acknowledgement_response.get('message') or ''
                except Exception:
                    status_text = ''
                append_ack_event(
                    receipts_root,
                    '',  # claim_key unknown here
                    status_text,
                    'API-277',
                    'uhcapi',
                    {'transactionId': transaction_id},
                    'api_ack',
                    int(time.time())
                )
        except Exception:
            pass
        
        return acknowledgement_response
 
    except Exception as e:
        print("Error during claim processing: {}".format(e))
        raise

# -----------------------------------------------------------------------------
# Helper: Optional acknowledgment (277CA) test endpoint
# -----------------------------------------------------------------------------

def test_acknowledgment(client, transaction_id, config, endpoint_name='UHCAPI'):
    """
    Light-weight probe to test the claim acknowledgment endpoint (e.g., 277CA) if configured.
    - Reads endpoint URL from config['MediLink_Config']['endpoints'][endpoint_name]['ack_endpoint']
    - Posts/gets with {'transactionId': transaction_id} depending on endpoint requirement
    - Logs response; returns parsed JSON or text.

    Backward-compatible: If no ack endpoint configured, logs and returns None without failing.
    """
    try:
        ack_url = (
            config.get('MediLink_Config', {})
                  .get('endpoints', {})
                  .get(endpoint_name, {})
                  .get('ack_endpoint')
        )
        if not ack_url:
            MediLink_ConfigLoader.log("Ack endpoint not configured for {}. Skipping acknowledgment test.".format(endpoint_name), level="INFO")
            return None

        payload = {"transactionId": transaction_id}
        headers = {"Content-Type": "application/json"}
        headers = client.add_environment_headers(headers, endpoint_name) if hasattr(client, 'add_environment_headers') else headers
        MediLink_ConfigLoader.log("Testing acknowledgment endpoint: {} payload={}".format(ack_url, payload), level="DEBUG")

        # Use generic request helper if available; otherwise fall back to requests
        try:
            response = client._request('post', ack_url, data=json.dumps(payload), headers=headers)  # type: ignore[attr-defined]
        except Exception:
            import requests as _rq
            response = _rq.post(ack_url, data=json.dumps(payload), headers=headers)
        
        try:
            content = response.json()
        except Exception:
            content = getattr(response, 'text', str(response))
        MediLink_ConfigLoader.log("Ack response: {}".format(content), level="INFO")
        return content
    except Exception as e:
        MediLink_ConfigLoader.log("Ack test failed: {}".format(e), level="ERROR")
        return None

if __name__ == "__main__":
    # Use factory for consistency but fallback to direct instantiation for testing
    try:
        from MediCafe.core_utils import get_api_client
        client = get_api_client()
        if client is None:
            client = APIClient()
    except ImportError:
        client = APIClient()
    
    # Define a configuration to enable or disable tests
    test_config = {
        'test_fetch_payer_name': False,
        'test_claim_summary': False,
        'test_eligibility': False,
        'test_eligibility_v3': False,
        'test_eligibility_super_connector': False,
        'test_claim_submission': False,
    }
    
    try:
        api_test_cases = client.config['MediLink_Config']['API Test Case']
        
        # Test 1: Fetch Payer Name
        if test_config.get('test_fetch_payer_name', False):
            try:
                for case in api_test_cases:
                    payer_name = fetch_payer_name_from_api(client, case['payer_id'], client.config)
                    print("*** TEST API: Payer Name: {}".format(payer_name))
            except Exception as e:
                print("*** TEST API: Error in Fetch Payer Name Test: {}".format(e))
        
        # Test 2: Get Claim Summary
        if test_config.get('test_claim_summary', False):
            try:
                for case in api_test_cases:
                    claim_summary = get_claim_summary_by_provider(client, case['provider_tin'], '05/01/2024', '06/23/2024', case['payer_id'])
                    print("TEST API: Claim Summary: {}".format(claim_summary))
            except Exception as e:
                print("TEST API: Error in Claim Summary Test: {}".format(e))
        
        # Test 3: Get Eligibility
        if test_config.get('test_eligibility', False):
            try:
                for case in api_test_cases:
                    eligibility = get_eligibility(client, case['payer_id'], case['provider_last_name'], case['search_option'], 
                                                  case['date_of_birth'], case['member_id'], case['npi'])
                    print("TEST API: Eligibility: {}".format(eligibility))
            except Exception as e:
                print("TEST API: Error in Eligibility Test: {}".format(e))

        # Test 4: Get Eligibility v3
        if test_config.get('test_eligibility_v3', False):
            try:
                for case in api_test_cases:
                    eligibility_v3 = get_eligibility_v3(client, payer_id=case['payer_id'], provider_last_name=case['provider_last_name'], 
                                                        search_option=case['search_option'], date_of_birth=case['date_of_birth'], 
                                                        member_id=case['member_id'], npi=case['npi'])
                    print("TEST API: Eligibility v3: {}".format(eligibility_v3))
            except Exception as e:
                print("TEST API: Error in Eligibility v3 Test: {}".format(e))

        # Test 5: Get Eligibility Super Connector (GraphQL)
        if test_config.get('test_eligibility_super_connector', False):
            try:
                for case in api_test_cases:
                    eligibility_super_connector = get_eligibility_super_connector(client, payer_id=case['payer_id'], provider_last_name=case['provider_last_name'], 
                                                                                search_option=case['search_option'], date_of_birth=case['date_of_birth'], 
                                                                                member_id=case['member_id'], npi=case['npi'])
                    print("TEST API: Eligibility Super Connector: {}".format(eligibility_super_connector))
            except Exception as e:
                print("TEST API: Error in Eligibility Super Connector Test: {}".format(e))

        """
        # Example of iterating over multiple patients (if needed)
        patients = [
            {'payer_id': '87726', 'provider_last_name': 'VIDA', 'search_option': 'MemberIDDateOfBirth', 'date_of_birth': '1980-01-01', 'member_id': '123456789', 'npi': '9876543210'},
            {'payer_id': '87726', 'provider_last_name': 'SMITH', 'search_option': 'MemberIDDateOfBirth', 'date_of_birth': '1970-02-02', 'member_id': '987654321', 'npi': '1234567890'},
            # Add more patients as needed
        ]

        for patient in patients:
            try:
                eligibility = get_eligibility(client, patient['payer_id'], patient['provider_last_name'], patient['search_option'], patient['date_of_birth'], patient['member_id'], patient['npi'])
                print("Eligibility for {}: {}".format(patient['provider_last_name'], eligibility))
            except Exception as e:
                print("Error in getting eligibility for {}: {}".format(patient['provider_last_name'], e))
        """
        # Test 6: UHC Claim Submission
        if test_config.get('test_claim_submission', False):
            try:
                x12_request_data = (
                    "ISA*00* *00* *ZZ*BRT219991205 *33*87726 *170417*1344*^*00501*019160001*0*P*:~GS*HC*BRT219991205*B2BRTA*20170417*134455*19160001*X*005010X222A1~ST*837*000000001*005010X222A1~BHT*0019*00*00001*20170417*134455*CH~NM1*41*2*B00099999819*****46*BB2B~PER*IC*NO NAME*TE*1234567890~NM1*40*2*TIGER*****46*87726~HL*1**20*1~NM1*85*2*XYZ ADDRESS*****XX*1073511762~N3*123 CITY#680~N4*STATE*TG*98765~REF*EI*943319804~PER*IC*XYZ ADDRESS*TE*8008738385*TE*9142862043*FX*1234567890~NM1*87*2~N3*PO BOX 277500~N4*STATE*TS*303847000~HL*2*1*22*0~SBR*P*18*701648******CI~NM1*IL*1*FNAME*LNAME****MI*00123456789~N3*2020 CITY~N4*STATE*TG*80001~DMG*D8*19820220*M~NM1*PR*2*PROVIDER XYZ*****PI*87726~\nCLM*TOSRTA-SPL1*471***12:B:1*Y*A*Y*Y*P~REF*D9*H4HZMH0R4P0104~HI*ABK:Z12~NM1*DN*1*DN*SKO****XX*1255589300~LX*1~SV1*HC:73525*471*UN*1***1~DTP*472*RD8*0190701-20190701~REF*6R*2190476543Z1~SE*30*000000001~GE*1*19160001~IEA*1*019160001~"
                )
                response = submit_uhc_claim(client, x12_request_data)
                print("\nTEST API: Claim Submission Response:\n", response)
            except Exception as e:
                print("\nTEST API: Error in Claim Submission Test:\n", e)
    
    except Exception as e:
        print("TEST API: Unexpected Error: {}".format(e))
