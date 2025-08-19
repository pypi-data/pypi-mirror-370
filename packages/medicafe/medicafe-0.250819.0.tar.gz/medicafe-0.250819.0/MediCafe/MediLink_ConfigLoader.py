# MediLink_ConfigLoader.py
import os, json, logging, sys, platform
try:
    import yaml
except ImportError:
    yaml = None
from datetime import datetime
from collections import OrderedDict

# Global configuration cache to prevent repeated loading
_CONFIG_CACHE = None
_CROSSWALK_CACHE = None

# Import centralized logging configuration
try:
    from MediCafe.logging_config import PERFORMANCE_LOGGING
except ImportError:
    # Fallback to local flag if centralized config is not available
    PERFORMANCE_LOGGING = False

def get_default_config():
    """Provide a default configuration when config files are missing."""
    return {
        'MediLink_Config': {
            'local_storage_path': '.',
            'receiptsRoot': './receipts',
            'api_endpoints': {
                'base_url': 'https://api.example.com',
                'timeout': 30
            },
            'logging': {
                'level': 'INFO',
                'console_output': True
            }
        }
    }

def get_default_crosswalk():
    """Provide a default crosswalk when crosswalk files are missing."""
    return {
        'insurance_types': {},
        'diagnosis_codes': {},
        'procedure_codes': {},
        'payer_mappings': {}
    }

"""
This function should be generalizable to have a initialization script over all the Medi* functions
"""
def load_configuration(config_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'config.json'), crosswalk_path=os.path.join(os.path.dirname(__file__), '..', 'json', 'crosswalk.json')):
    """
    Loads endpoint configuration, credentials, and other settings from JSON or YAML files.
        
    Returns: A tuple containing dictionaries with configuration settings for the main config and crosswalk.
    """
    global _CONFIG_CACHE, _CROSSWALK_CACHE
    
    # Return cached configuration if available
    if _CONFIG_CACHE is not None and _CROSSWALK_CACHE is not None:
        return _CONFIG_CACHE, _CROSSWALK_CACHE
    
    import time
    config_start = time.time()
    if PERFORMANCE_LOGGING:
        print("Configuration loading started...")
    
    # TODO (Low Config Upgrade) The Medicare / Private differentiator flag probably needs to be pulled or passed to this.
    # SUGGESTION:
    # - Introduce optional keys under MediLink_Config: {'payer_type': 'Medicare'|'Private'} or per-endpoint flags.
    # - Keep behavior identical when key is absent. Only consumers that opt-in should read this.
    # - XP note: keep the structure flat to avoid deep dict traversal when used in hot paths.
    # Use provided paths, or fall back to platform-specific defaults
    path_check_start = time.time()
    if not os.path.exists(config_path):
        # Try platform-specific paths as fallback
        if platform.system() == 'Windows' and platform.release() == 'XP':
            # Use F: paths for Windows XP
            config_path = "F:\\Medibot\\json\\config.json"
            crosswalk_path = "F:\\Medibot\\json\\crosswalk.json"
        elif platform.system() == 'Windows':
            # Use current working directory for other versions of Windows
            current_dir = os.getcwd()
            config_path = os.path.join(current_dir, 'json', 'config.json')
            crosswalk_path = os.path.join(current_dir, 'json', 'crosswalk.json')
        # If not Windows or if local files don't exist, keep the default paths
    
    path_check_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Path resolution completed in {:.2f} seconds".format(path_check_end - path_check_start))
    
    # Load configuration with graceful fallback
    config = None
    crosswalk = None
    
    try:
        config_load_start = time.time()
        with open(config_path, 'r') as config_file:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(config_file)
            elif config_path.endswith('.json'):
                config = json.load(config_file, object_pairs_hook=OrderedDict)
            else:
                raise ValueError("Unsupported configuration format.")
            
            if 'MediLink_Config' not in config:
                raise KeyError("MediLink_Config key is missing from the loaded configuration.")
        
        config_load_end = time.time()
        if PERFORMANCE_LOGGING:
            print("Config file loading completed in {:.2f} seconds".format(config_load_end - config_load_start))

        # FUTURE: centralize crosswalk writes for atomic updates from encoder flows
        # e.g., def save_crosswalk(crosswalk): write temp file then replace to avoid partial writes on XP.
        crosswalk_load_start = time.time()
        with open(crosswalk_path, 'r') as crosswalk_file:
            crosswalk = json.load(crosswalk_file)
        crosswalk_load_end = time.time()
        if PERFORMANCE_LOGGING:
            print("Crosswalk file loading completed in {:.2f} seconds".format(crosswalk_load_end - crosswalk_load_start))

    except FileNotFoundError:
        # Graceful fallback to default configurations
        print("Configuration files not found. Using default configurations.")
        print("Config path: {}, Crosswalk path: {}".format(config_path, crosswalk_path))
        print("To use custom configurations, create the 'json' directory and add config.json and crosswalk.json files.")
        
        config = get_default_config()
        crosswalk = get_default_crosswalk()
        
        # Log the fallback for debugging
        if PERFORMANCE_LOGGING:
            print("Using default configurations due to missing files")
            
    except ValueError as e:
        if isinstance(e, UnicodeDecodeError):
            print("Error decoding file: {}".format(e))
        else:
            print("Error parsing file: {}".format(e))
        print("Falling back to default configurations...")
        config = get_default_config()
        crosswalk = get_default_crosswalk()
    except KeyError as e:
        print("Critical configuration is missing: {}".format(e))
        print("Falling back to default configurations...")
        config = get_default_config()
        crosswalk = get_default_crosswalk()
    except Exception as e:
        print("An unexpected error occurred while loading the configuration: {}".format(e))
        print("Falling back to default configurations...")
        config = get_default_config()
        crosswalk = get_default_crosswalk()

    config_end = time.time()
    if PERFORMANCE_LOGGING:
        print("Total configuration loading completed in {:.2f} seconds".format(config_end - config_start))
    
    # Cache the loaded configuration
    _CONFIG_CACHE = config
    _CROSSWALK_CACHE = crosswalk
    
    return config, crosswalk

def clear_config_cache():
    """Clear the configuration cache to force reloading on next call."""
    global _CONFIG_CACHE, _CROSSWALK_CACHE
    _CONFIG_CACHE = None
    _CROSSWALK_CACHE = None
        
# Logs messages with optional error type and claim data.
def log(message, config=None, level="INFO", error_type=None, claim=None, verbose=False, console_output=False):
    
    # If config is not provided, use cached config or load it
    if config is None:
        try:
            if _CONFIG_CACHE is None:
                config, _ = load_configuration()
            else:
                config = _CONFIG_CACHE
        except BaseException:
            # Configuration unavailable; fall back to minimal console logging
            config = {}
    
    # Setup logger if not already configured
    if not logging.root.handlers:
        local_storage_path = '.'
        if isinstance(config, dict):
            try:
                local_storage_path = config.get('MediLink_Config', {}).get('local_storage_path', '.')
            except Exception:
                local_storage_path = '.'
        log_filename = datetime.now().strftime("Log_%m%d%Y.log")
        log_filepath = os.path.join(local_storage_path, log_filename)
        
        # Set logging level based on verbosity
        logging_level = logging.DEBUG if verbose else logging.INFO
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        handlers = []
        try:
            # Create file handler when path is usable
            file_handler = logging.FileHandler(log_filepath, mode='a')
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception:
            # Fall back to console-only if file handler cannot be created
            pass
        
        # Add console handler only if console_output is True
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)
        
        # If no handlers could be added (e.g., file path invalid and console_output False), add a console handler
        if not handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            handlers.append(console_handler)
        
        logging.basicConfig(level=logging_level, handlers=handlers)
    
    # Prepare log message
    claim_data = " - Claim Data: {}".format(claim) if claim else ""
    error_info = " - Error Type: {}".format(error_type) if error_type else ""
    full_message = "{} {}{}".format(message, claim_data, error_info)

    # Log the message
    logger = logging.getLogger()
    getattr(logger, level.lower())(full_message)