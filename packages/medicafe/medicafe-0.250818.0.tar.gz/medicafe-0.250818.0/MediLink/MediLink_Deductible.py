"""
# Create a summary JSON
summary = {
    "Payer ID": ins_payerID,
    "Provider": provider_last_name,
    "Member ID": ins_memberID,
    "Date of Birth": dob,
    "Patient Name": patient_name,
    "Patient Info": {
        "DOB": dob,
        "Address": "{} {}".format(patient_info.get("addressLine1", ""), patient_info.get("addressLine2", "")).strip(),
        "City": patient_info.get("city", ""),
        "State": patient_info.get("state", ""),
        "ZIP": patient_info.get("zip", ""),
        "Relationship": patient_info.get("relationship", "")
    },
    "Insurance Info": {
        "Payer Name": insurance_info.get("payerName", ""),
        "Payer ID": ins_payerID,
        "Member ID": ins_memberID,
        "Group Number": insurance_info.get("groupNumber", ""),
        "Insurance Type": ins_insuranceType,
        "Type Code": ins_insuranceTypeCode,
        "Address": "{} {}".format(insurance_info.get("addressLine1", ""), insurance_info.get("addressLine2", "")).strip(),
        "City": insurance_info.get("city", ""),
        "State": insurance_info.get("state", ""),
        "ZIP": insurance_info.get("zip", "")
    },
    "Policy Info": {
        "Eligibility Dates": eligibilityDates,
        "Policy Member ID": policy_info.get("memberId", ""),
        "Policy Status": policy_status
    },
    "Deductible Info": {
        "Remaining Amount": remaining_amount
    }
}

Features Added:
1. Allows users to manually input patient information for deductible lookup before processing CSV data.
2. Supports multiple manual requests, each generating its own Notepad file.
3. Validates user inputs and provides feedback on required formats.
4. Displays available Payer IDs as a note after manual entries.

UPGRADED TO LATEST CORE_UTILS:
- Uses setup_project_path() for standardized path management
- Uses get_api_core_client() for improved API client handling
- Uses create_config_cache() for better performance
- Uses log_import_error() for enhanced error logging
- Improved import error handling with fallbacks
"""
# MediLink_Deductible.py
import os, sys, json
from datetime import datetime

# Add parent directory to Python path to access MediCafe module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Use latest core_utils for standardized setup and imports
try:
    from MediCafe.core_utils import (
        setup_project_path, 
        get_shared_config_loader, 
        get_api_core_client,
        log_import_error,
        create_config_cache
    )
    # Set up project paths using latest core_utils
    project_dir = setup_project_path(__file__)
    MediLink_ConfigLoader = get_shared_config_loader()

    # Import api_core for eligibility functions
    try:
        from MediCafe import api_core
    except ImportError:
        api_core = None
    
    # Import api_core for eligibility functions
    try:
        from MediCafe import api_core
    except ImportError:
        api_core = None
    
    # Import api_core for eligibility functions
    try:
        from MediCafe import api_core
    except ImportError:
        api_core = None
except ImportError as e:
    print("Error: Unable to import MediCafe.core_utils. Please ensure MediCafe package is properly installed.")
    # Don't call log_import_error here since it's not available yet
    print("Import error: {}".format(e))
    sys.exit(1)

# Safe import for requests with fallback
try:
    import requests
except ImportError:
    requests = None
    print("Warning: requests module not available. Some API functionality may be limited.")

try:
    from MediLink import MediLink_Deductible_Validator
except ImportError as e:
    print("Warning: Unable to import MediLink_Deductible_Validator: {}".format(e))
    import MediLink_Deductible_Validator

try:
    from MediBot import MediBot_Preprocessor_lib
except ImportError as e:
    print("Warning: Unable to import MediBot_Preprocessor_lib: {}".format(e))
    import MediBot_Preprocessor_lib

# Function to check if the date format is correct
def validate_and_format_date(date_str):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%d-%m-%Y'):
        try:
            formatted_date = datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            return formatted_date
        except ValueError:
            continue
    return None

# Use latest core_utils configuration cache for better performance
_get_config, (_config_cache, _crosswalk_cache) = create_config_cache()

# Load configuration using latest core_utils pattern
config, _ = _get_config()

# Initialize the API client using latest core_utils
client = get_api_core_client()
if client is None:
    print("Warning: API client not available via core_utils")
    # Fallback to direct instantiation
    try:
        if api_core:
            client = api_core.APIClient()
        else:
            raise ImportError("api_core not available")
    except ImportError as e:
        print("Error: Unable to create API client: {}".format(e))
        client = None

# Get provider_last_name and npi from configuration
provider_last_name = config['MediLink_Config'].get('default_billing_provider_last_name', 'Unknown')
npi = config['MediLink_Config'].get('default_billing_provider_npi', 'Unknown')

# Check if the provider_last_name is still 'Unknown'
if provider_last_name == 'Unknown':
    MediLink_ConfigLoader.log("Warning: provider_last_name was not found in the configuration.", level="WARNING")

# Define the list of payer_id's to iterate over
payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '06111', '37602']  # United Healthcare.

# Get the latest CSV
CSV_FILE_PATH = config.get('CSV_FILE_PATH', "")
csv_data = MediBot_Preprocessor_lib.load_csv_data(CSV_FILE_PATH)

# Only keep rows that have an exact match with a payer ID from the payer_ids list
valid_rows = [row for row in csv_data if str(row.get('Ins1 Payer ID', '')).strip() in payer_ids]

# Extract important columns for summary with fallback
summary_valid_rows = [
    {
        'DOB': row.get('Patient DOB', row.get('DOB', '')),  # Try 'Patient DOB' first, then 'DOB'
        'Ins1 Member ID': row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip(),  # Try 'Primary Policy Number' first, then 'Ins1 Member ID'
        'Ins1 Payer ID': row.get('Ins1 Payer ID', '')
    }
    for row in valid_rows
]

# Print summary of valid rows
print("\n--- Summary of Valid Rows ---")
for row in summary_valid_rows:
    print("DOB: {}, Member ID: {}, Payer ID: {}".format(row['DOB'], row['Ins1 Member ID'], row['Ins1 Payer ID']))

# List of patients with DOB and MemberID from CSV data with fallback
patients = [
    (validate_and_format_date(row.get('Patient DOB', row.get('DOB', ''))),  # Try 'Patient DOB' first, then 'DOB'
     row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip())  # Try 'Primary Policy Number' first, then 'Ins1 Member ID'
    for row in valid_rows 
    if validate_and_format_date(row.get('Patient DOB', row.get('DOB', ''))) is not None and 
       row.get('Primary Policy Number', row.get('Ins1 Member ID', '')).strip()
]

# Function to handle manual patient deductible lookup
def manual_deductible_lookup():
    print("\n--- Manual Patient Deductible Lookup ---")
    print("Available Payer IDs: {}".format(", ".join(payer_ids)))
    print("Enter 'quit' at any time to return to main menu.\n")
    
    while True:
        member_id = input("Enter the Member ID of the subscriber (or 'quit' to exit): ").strip()
        if member_id.lower() == 'quit':
            print("Returning to main menu.\n")
            break
        if not member_id:
            print("No Member ID entered. Please try again.\n")
            continue

        dob_input = input("Enter the Date of Birth (YYYY-MM-DD): ").strip()
        if dob_input.lower() == 'quit':
            print("Returning to main menu.\n")
            break
            
        formatted_dob = validate_and_format_date(dob_input)
        if not formatted_dob:
            print("Invalid DOB format. Please enter in YYYY-MM-DD format.\n")
            continue

        print("\nProcessing manual lookup for Member ID: {}, DOB: {}".format(member_id, formatted_dob))
        print("Checking {} payer IDs...".format(len(payer_ids)))

        # Fetch eligibility data
        found_data = False
        for i, payer_id in enumerate(payer_ids, 1):
            print("Checking Payer ID {} ({}/{}): {}".format(payer_id, i, len(payer_ids), payer_id))
            
            # Use the current mode setting for validation
            run_validation = DEBUG_MODE
            eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, formatted_dob, member_id, npi, run_validation=run_validation)
            if eligibility_data:
                found_data = True
                # Generate unique output file for manual request
                output_file_name = "eligibility_report_manual_{}_{}.txt".format(member_id, formatted_dob)
                output_file_path = os.path.join(os.getenv('TEMP'), output_file_name)
                with open(output_file_path, 'w') as output_file:
                    table_header = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                        "Patient Name", "DOB", "Insurance Type", "PayID", "Policy Status", "Remaining Amt")
                    output_file.write(table_header + "\n")
                    output_file.write("-" * len(table_header) + "\n")
                    print(table_header)
                    print("-" * len(table_header))
                    display_eligibility_info(eligibility_data, formatted_dob, member_id, output_file)
                
                # Ask if user wants to open the report
                open_report = input("\nEligibility data found! Open the report? (Y/N): ").strip().lower()
                if open_report in ['y', 'yes']:
                    os.system('notepad.exe "{}"'.format(output_file_path))
                print("Manual eligibility report generated: {}\n".format(output_file_path))
                break  # Assuming one payer ID per manual lookup
            else:
                print("No eligibility data found for Payer ID: {}".format(payer_id))
        
        if not found_data:
            print("\nNo eligibility data found for any Payer ID.")
        
        # Ask if the user wants to perform another manual lookup
        continue_choice = input("\nDo you want to perform another manual lookup? (Y/N): ").strip().lower()
        if continue_choice in ['n', 'no']:
            break


# Function to get eligibility information
def get_eligibility_info(client, payer_id, provider_last_name, date_of_birth, member_id, npi, run_validation=False):
    try:
        # Log the parameters being sent to the function
        MediLink_ConfigLoader.log("Calling eligibility check with parameters:", level="DEBUG")
        MediLink_ConfigLoader.log("payer_id: {}".format(payer_id), level="DEBUG")
        MediLink_ConfigLoader.log("provider_last_name: {}".format(provider_last_name), level="DEBUG")
        MediLink_ConfigLoader.log("date_of_birth: {}".format(date_of_birth), level="DEBUG")
        MediLink_ConfigLoader.log("member_id: {}".format(member_id), level="DEBUG")
        MediLink_ConfigLoader.log("npi: {}".format(npi), level="DEBUG")

        # Check if we're in legacy mode (no validation) or debug mode (with validation)
        if run_validation:
            # Debug mode: Call both APIs and run validation
            MediLink_ConfigLoader.log("Running in DEBUG MODE - calling both APIs", level="INFO")
            
            # Get legacy response
            MediLink_ConfigLoader.log("Getting legacy get_eligibility_v3 API response", level="INFO")
            legacy_eligibility = api_core.get_eligibility_v3(
                client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
            )
            
            # Get Super Connector response for comparison
            MediLink_ConfigLoader.log("Getting new get_eligibility_super_connector API response", level="INFO")
            super_connector_eligibility = None
            try:
                super_connector_eligibility = api_core.get_eligibility_super_connector(
                    client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
                )
            except Exception as e:
                MediLink_ConfigLoader.log("Super Connector API failed: {}".format(e), level="ERROR")
            
            # Run validation if we have both responses
            if legacy_eligibility and super_connector_eligibility:
                validation_file_path = os.path.join(os.getenv('TEMP'), 'validation_report_{}_{}.txt'.format(member_id, date_of_birth))
                validation_report = MediLink_Deductible_Validator.run_validation_comparison(
                    legacy_eligibility, super_connector_eligibility, validation_file_path
                )
                print("\nValidation report generated: {}".format(validation_file_path))
                
                # Log any Super Connector API errors
                if "rawGraphQLResponse" in super_connector_eligibility:
                    raw_response = super_connector_eligibility.get('rawGraphQLResponse', {})
                    errors = raw_response.get('errors', [])
                    if errors:
                        print("Super Connector API returned {} error(s):".format(len(errors)))
                        for i, error in enumerate(errors):
                            error_code = error.get('code', 'UNKNOWN')
                            error_desc = error.get('description', 'No description')
                            print("  Error {}: {} - {}".format(i+1, error_code, error_desc))
                            
                            # Check for data in error extensions (some APIs return data here)
                            extensions = error.get('extensions', {})
                            if extensions and 'details' in extensions:
                                details = extensions.get('details', [])
                                if details:
                                    print("    Found {} detail records in error extensions".format(len(details)))
                                    # Log first detail record for debugging
                                    if details:
                                        first_detail = details[0]
                                        print("    First detail: {}".format(first_detail))
                
                    # Check status code
                    status_code = super_connector_eligibility.get('statuscode')
                    if status_code and status_code != '200':
                        print("Super Connector API status code: {} (non-200 indicates errors)".format(status_code))
                
                # Open validation report in Notepad
                os.system('notepad.exe "{}"'.format(validation_file_path))
            
            # Return legacy response for consistency
            eligibility = legacy_eligibility
            
        else:
            # Legacy mode: Only call legacy API
            MediLink_ConfigLoader.log("Running in LEGACY MODE - calling legacy API only", level="INFO")
            
            # Only get legacy response
            MediLink_ConfigLoader.log("Getting legacy get_eligibility_v3 API response", level="INFO")
            eligibility = api_core.get_eligibility_v3(
                client, payer_id, provider_last_name, 'MemberIDDateOfBirth', date_of_birth, member_id, npi
            )
        
        # Log the response
        MediLink_ConfigLoader.log("Eligibility response: {}".format(json.dumps(eligibility, indent=4)), level="DEBUG")
        
        return eligibility
    except Exception as e:
        # Handle HTTP errors if requests is available
        if requests and hasattr(requests, 'exceptions') and isinstance(e, requests.exceptions.HTTPError):
            # Log the HTTP error response
            print("API Request Error: {}".format(e))
            if hasattr(e, 'response') and hasattr(e.response, 'content'):
                MediLink_ConfigLoader.log("Response content: {}".format(e.response.content), level="ERROR")
        else:
            # Log any other exceptions
            print("Eligibility Check Error: {}".format(e))
    return None

# Helper functions to extract data from different API response formats
# TODO (HIGH PRIORITY - API Response Parser Debugging):
# PROBLEM: API responses are returning correctly but the parser functions below 
# are not successfully extracting the super_connector variables (likely eligibility data).
# This suggests a schema mismatch between expected and actual API response format.
#
# IMPLEMENTATION CLARIFICATION:
# - Primary path should not depend on probing payer_ids via API.
# - Prefer payer_id provided by CSV/crosswalk as the authoritative source.
# - Keep API probing behind a non-default debug flag to support troubleshooting sessions only.
# - Add detailed logging helpers (no-op in production) to inspect mismatches safely on XP.
#
# DEBUGGING STEPS:
# 1. Response Structure Analysis:
#    - Add comprehensive logging of raw API responses before parsing
#    - Compare current response format vs expected format in parser functions
#    - Check if API endpoint has changed response schema recently
#    - Verify if different endpoints return different response structures
#
# 2. Parser Function Validation:
#    - Test each extract_*_patient_info() function with sample responses
#    - Check if field names/paths have changed (e.g., 'patientInfo' vs 'patient_info')
#    - Verify array indexing logic (e.g., [0] access on empty arrays)
#    - Check case sensitivity in field access
#
# 3. Super Connector Variable Mapping:
#    - Document what "super_connector variables" should contain
#    - Identify which fields from API response map to these variables
#    - Verify the expected format vs actual format
#    - Check if variable names have changed in the application
#
# IMPLEMENTATION PLAN:
# 1. Enhanced Logging:
#    - Add log_api_response_structure(response) function
#    - Log raw JSON before each parser function call
#    - Add field-by-field parsing logs with null checks
#
# 2. Parser Robustness:
#    - Add null/empty checks for all field accesses
#    - Implement graceful fallbacks for missing fields
#    - Add validation for expected data types
#    - Handle both old and new response formats if schema changed
#
# 3. Schema Validation:
#    - Create validate_api_response_schema(response, expected_schema) function
#    - Define expected schemas for each API endpoint
#    - Alert when response doesn't match expected schema
#    - Suggest schema updates when mismatches occur
#
# 4. Testing Framework:
#    - Create test cases with known good API responses
#    - Test parser functions independently of API calls
#    - Add integration tests for end-to-end parsing workflow
#    - Create mock responses for development testing
#
# IMMEDIATE ACTIONS:
# 1. Add detailed logging before each extract_*_patient_info() call
# 2. Log the structure of the 'policy' object being passed to parsers
# 3. Check if the issue is in extract_legacy_patient_info() vs extract_super_connector_patient_info()
# 4. Verify which API endpoint is being called and if it matches expected parser
#
# FILES TO EXAMINE:
# - This file: all extract_*_patient_info() functions
# - MediCafe/api_core.py: API call implementation and response handling
# - Config files: Check if API endpoints or credentials have changed
#
# RELATED ISSUES:
# - May be connected to authentication or endpoint configuration problems
# - Could indicate API version updates that changed response format
# - Might be related to different payer-specific response formats

def extract_legacy_patient_info(policy):
    """Extract patient information from legacy API response format"""
    patient_info = policy.get("patientInfo", [{}])[0]
    return {
        'lastName': patient_info.get("lastName", ""),
        'firstName': patient_info.get("firstName", ""),
        'middleName': patient_info.get("middleName", "")
    }

def extract_super_connector_patient_info(eligibility_data):
    """Extract patient information from Super Connector API response format"""
    if not eligibility_data:
        return {'lastName': '', 'firstName': '', 'middleName': ''}
    
    # Handle multiple eligibility records - use the first one with valid data
    if "rawGraphQLResponse" in eligibility_data:
        raw_response = eligibility_data.get('rawGraphQLResponse', {})
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try to get from the first eligibility record
        if eligibility_list:
            first_eligibility = eligibility_list[0]
            member_info = first_eligibility.get('eligibilityInfo', {}).get('member', {})
            if member_info:
                return {
                    'lastName': member_info.get("lastName", ""),
                    'firstName': member_info.get("firstName", ""),
                    'middleName': member_info.get("middleName", "")
                }
        
        # Check for data in error extensions (some APIs return data here despite errors)
        errors = raw_response.get('errors', [])
        for error in errors:
            extensions = error.get('extensions', {})
            if extensions and 'details' in extensions:
                details = extensions.get('details', [])
                if details:
                    # Use the first detail record that has patient info
                    for detail in details:
                        if detail.get('lastName') or detail.get('firstName'):
                            return {
                                'lastName': detail.get("lastName", ""),
                                'firstName': detail.get("firstName", ""),
                                'middleName': detail.get("middleName", "")
                            }
    
    # Fallback to top-level fields
    return {
        'lastName': eligibility_data.get("lastName", ""),
        'firstName': eligibility_data.get("firstName", ""),
        'middleName': eligibility_data.get("middleName", "")
    }

def extract_legacy_remaining_amount(policy):
    """Extract remaining amount from legacy API response format"""
    deductible_info = policy.get("deductibleInfo", {})
    if 'individual' in deductible_info:
        remaining = deductible_info['individual']['inNetwork'].get("remainingAmount", "")
        return remaining if remaining else "Not Found"
    elif 'family' in deductible_info:
        remaining = deductible_info['family']['inNetwork'].get("remainingAmount", "")
        return remaining if remaining else "Not Found"
    else:
        return "Not Found"

def extract_super_connector_remaining_amount(eligibility_data):
    """Extract remaining amount from Super Connector API response format"""
    if not eligibility_data:
        return "Not Found"
    
    # First, check top-level metYearToDateAmount which might indicate deductible met
    met_amount = eligibility_data.get('metYearToDateAmount')
    if met_amount is not None:
        return str(met_amount)
    
    # Collect all deductible amounts to find the most relevant one
    all_deductible_amounts = []
    
    # Look for deductible information in planLevels (based on validation report)
    plan_levels = eligibility_data.get('planLevels', [])
    for plan_level in plan_levels:
        if plan_level.get('level') == 'deductibleInfo':
            # Collect individual deductible amounts
            individual_levels = plan_level.get('individual', [])
            if individual_levels:
                for individual in individual_levels:
                    remaining = individual.get('remainingAmount')
                    if remaining is not None:
                        try:
                            amount = float(remaining)
                            all_deductible_amounts.append(('individual', amount))
                        except (ValueError, TypeError):
                            pass
            
            # Collect family deductible amounts
            family_levels = plan_level.get('family', [])
            if family_levels:
                for family in family_levels:
                    remaining = family.get('remainingAmount')
                    if remaining is not None:
                        try:
                            amount = float(remaining)
                            all_deductible_amounts.append(('family', amount))
                        except (ValueError, TypeError):
                            pass
    
    # Navigate to the rawGraphQLResponse structure as fallback
    raw_response = eligibility_data.get('rawGraphQLResponse', {})
    if raw_response:
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try all eligibility records for deductible information
        for eligibility in eligibility_list:
            plan_levels = eligibility.get('eligibilityInfo', {}).get('planLevels', [])
            for plan_level in plan_levels:
                if plan_level.get('level') == 'deductibleInfo':
                    # Collect individual deductible amounts
                    individual_levels = plan_level.get('individual', [])
                    if individual_levels:
                        for individual in individual_levels:
                            remaining = individual.get('remainingAmount')
                            if remaining is not None:
                                try:
                                    amount = float(remaining)
                                    all_deductible_amounts.append(('individual', amount))
                                except (ValueError, TypeError):
                                    pass
                    
                    # Collect family deductible amounts
                    family_levels = plan_level.get('family', [])
                    if family_levels:
                        for family in family_levels:
                            remaining = family.get('remainingAmount')
                            if remaining is not None:
                                try:
                                    amount = float(remaining)
                                    all_deductible_amounts.append(('family', amount))
                                except (ValueError, TypeError):
                                    pass
    
    # Select the most relevant deductible amount
    if all_deductible_amounts:
        # Strategy: Prefer individual over family, and prefer non-zero amounts
        # First, try to find non-zero individual amounts
        non_zero_individual = [amt for type_, amt in all_deductible_amounts if type_ == 'individual' and amt > 0]
        if non_zero_individual:
            return str(max(non_zero_individual))  # Return highest non-zero individual amount
        
        # If no non-zero individual, try non-zero family amounts
        non_zero_family = [amt for type_, amt in all_deductible_amounts if type_ == 'family' and amt > 0]
        if non_zero_family:
            return str(max(non_zero_family))  # Return highest non-zero family amount
        
        # If all amounts are zero, return the first individual amount (or family if no individual)
        individual_amounts = [amt for type_, amt in all_deductible_amounts if type_ == 'individual']
        if individual_amounts:
            return str(individual_amounts[0])
        
        # Fallback to first family amount
        family_amounts = [amt for type_, amt in all_deductible_amounts if type_ == 'family']
        if family_amounts:
            return str(family_amounts[0])
    
    return "Not Found"

def extract_legacy_insurance_info(policy):
    """Extract insurance information from legacy API response format"""
    insurance_info = policy.get("insuranceInfo", {})
    return {
        'insuranceType': insurance_info.get("insuranceType", ""),
        'insuranceTypeCode': insurance_info.get("insuranceTypeCode", ""),
        'memberId': insurance_info.get("memberId", ""),
        'payerId': insurance_info.get("payerId", "")
    }

def extract_super_connector_insurance_info(eligibility_data):
    """Extract insurance information from Super Connector API response format"""
    if not eligibility_data:
        return {'insuranceType': '', 'insuranceTypeCode': '', 'memberId': '', 'payerId': ''}
    
    # Handle multiple eligibility records - use the first one with valid data
    if "rawGraphQLResponse" in eligibility_data:
        raw_response = eligibility_data.get('rawGraphQLResponse', {})
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try to get from the first eligibility record
        if eligibility_list:
            first_eligibility = eligibility_list[0]
            insurance_info = first_eligibility.get('eligibilityInfo', {}).get('insuranceInfo', {})
            if insurance_info:
                return {
                    'insuranceType': insurance_info.get("planTypeDescription", ""),
                    'insuranceTypeCode': insurance_info.get("productServiceCode", ""),
                    'memberId': insurance_info.get("memberId", ""),
                    'payerId': insurance_info.get("payerId", "")
                }
        
        # Check for data in error extensions (some APIs return data here despite errors)
        errors = raw_response.get('errors', [])
        for error in errors:
            extensions = error.get('extensions', {})
            if extensions and 'details' in extensions:
                details = extensions.get('details', [])
                if details:
                    # Use the first detail record that has insurance info
                    for detail in details:
                        if detail.get('memberId') or detail.get('payerId'):
                            # Try to determine insurance type from available data
                            insurance_type = detail.get('planType', '')
                            if not insurance_type:
                                insurance_type = detail.get('productType', '')
                            
                            return {
                                'insuranceType': insurance_type,
                                'insuranceTypeCode': detail.get("productServiceCode", ""),
                                'memberId': detail.get("memberId", ""),
                                'payerId': detail.get("payerId", "")
                            }
    
    # Fallback to top-level fields
    insurance_type = eligibility_data.get("planTypeDescription", "")
    if not insurance_type:
        insurance_type = eligibility_data.get("productType", "")
    
    # Clean up the insurance type if it's too long (like the LPPO description)
    if insurance_type and len(insurance_type) > 50:
        # Extract just the plan type part
        if "PPO" in insurance_type:
            insurance_type = "Preferred Provider Organization (PPO)"
        elif "HMO" in insurance_type:
            insurance_type = "Health Maintenance Organization (HMO)"
        elif "EPO" in insurance_type:
            insurance_type = "Exclusive Provider Organization (EPO)"
        elif "POS" in insurance_type:
            insurance_type = "Point of Service (POS)"
    
    # Get insurance type code from multiple possible locations
    insurance_type_code = eligibility_data.get("productServiceCode", "")
    if not insurance_type_code:
        # Try to get from coverageTypes
        coverage_types = eligibility_data.get("coverageTypes", [])
        if coverage_types:
            insurance_type_code = coverage_types[0].get("typeCode", "")
    
    # Note: We're not mapping "M" to "PR" as "M" likely means "Medical" 
    # and "PR" should be "12" for PPO according to CMS standards
    # This mapping should be handled by the API developers
    
    return {
        'insuranceType': insurance_type,
        'insuranceTypeCode': insurance_type_code,
        'memberId': eligibility_data.get("subscriberId", ""),
        'payerId': eligibility_data.get("payerId", "")  # Use payerId instead of legalEntityCode (this should be payer_id from the inputs)
    }

def extract_legacy_policy_status(policy):
    """Extract policy status from legacy API response format"""
    policy_info = policy.get("policyInfo", {})
    return policy_info.get("policyStatus", "")

def extract_super_connector_policy_status(eligibility_data):
    """Extract policy status from Super Connector API response format"""
    if not eligibility_data:
        return ""
    
    # Handle multiple eligibility records - use the first one with valid data
    if "rawGraphQLResponse" in eligibility_data:
        raw_response = eligibility_data.get('rawGraphQLResponse', {})
        data = raw_response.get('data', {})
        check_eligibility = data.get('checkEligibility', {})
        eligibility_list = check_eligibility.get('eligibility', [])
        
        # Try to get from the first eligibility record
        if eligibility_list:
            first_eligibility = eligibility_list[0]
            insurance_info = first_eligibility.get('eligibilityInfo', {}).get('insuranceInfo', {})
            if insurance_info:
                return insurance_info.get("policyStatus", "")
    
    # Fallback to top-level field
    return eligibility_data.get("policyStatus", "")

def is_legacy_response_format(data):
    """Determine if the response is in legacy format (has memberPolicies)"""
    return data is not None and "memberPolicies" in data

def is_super_connector_response_format(data):
    """Determine if the response is in Super Connector format (has rawGraphQLResponse)"""
    return data is not None and "rawGraphQLResponse" in data

# Function to extract required fields and display in a tabular format
def display_eligibility_info(data, dob, member_id, output_file):
    if data is None:
        return

    # Determine which API response format we're dealing with
    if is_legacy_response_format(data):
        # Handle legacy API response format
        for policy in data.get("memberPolicies", []):
            # Skip non-medical policies
            if policy.get("policyInfo", {}).get("coverageType", "") != "Medical":
                continue

            patient_info = extract_legacy_patient_info(policy)
            remaining_amount = extract_legacy_remaining_amount(policy)
            insurance_info = extract_legacy_insurance_info(policy)
            policy_status = extract_legacy_policy_status(policy)

            patient_name = "{} {} {}".format(
                patient_info['firstName'], 
                patient_info['middleName'], 
                patient_info['lastName']
            ).strip()[:20]

            # Display patient information in a table row format
            table_row = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                patient_name, dob, insurance_info['insuranceType'], 
                insurance_info['payerId'], policy_status, remaining_amount)
            output_file.write(table_row + "\n")
            print(table_row)  # Print to console for progressive display

    elif is_super_connector_response_format(data):
        # Handle Super Connector API response format
        patient_info = extract_super_connector_patient_info(data)
        remaining_amount = extract_super_connector_remaining_amount(data)
        insurance_info = extract_super_connector_insurance_info(data)
        policy_status = extract_super_connector_policy_status(data)

        patient_name = "{} {} {}".format(
            patient_info['firstName'], 
            patient_info['middleName'], 
            patient_info['lastName']
        ).strip()[:20]

        # Display patient information in a table row format
        table_row = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
            patient_name, dob, insurance_info['insuranceType'], 
            insurance_info['payerId'], policy_status, remaining_amount)
        output_file.write(table_row + "\n")
        print(table_row)  # Print to console for progressive display

    else:
        # Unknown response format - log for debugging
        MediLink_ConfigLoader.log("Unknown response format in display_eligibility_info", level="WARNING")
        MediLink_ConfigLoader.log("Response structure: {}".format(json.dumps(data, indent=2)), level="DEBUG")

# Global mode flags (will be set in main)
LEGACY_MODE = False
DEBUG_MODE = False

# Main Execution Flow
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MEDILINK DEDUCTIBLE LOOKUP TOOL")
    print("=" * 80)
    print("This tool provides manual and batch eligibility lookups.")
    print("=" * 80)
    
    # User input switch for mode selection
    print("\nSelect operation mode:")
    print("1. Legacy Mode (Default) - Single API calls, consolidated output")
    print("2. Debug Mode - Dual API calls with validation reports")
    print("3. Exit")
    
    mode_choice = input("\nEnter your choice (1-3) [Default: 1]: ").strip()
    if not mode_choice:
        mode_choice = "1"
    
    if mode_choice == "3":
        print("\nExiting. Thank you for using MediLink Deductible Tool!")
        sys.exit(0)
    elif mode_choice not in ["1", "2"]:
        print("Invalid choice. Using Legacy Mode (Default).")
        mode_choice = "1"
    
    # Set mode flags
    LEGACY_MODE = (mode_choice == "1")
    DEBUG_MODE = (mode_choice == "2")
    
    if LEGACY_MODE:
        print("\nRunning in LEGACY MODE")
        print("- Single API calls (Legacy API only)")
        print("- Progressive output during processing")
        print("- Consolidated output file at the end")
    else:
        print("\nRunning in DEBUG MODE")
        print("- Dual API calls (Legacy + Super Connector)")
        print("- Validation reports and comparisons")
        print("- Detailed logging and error reporting")
    
    while True:
        print("\nChoose an option:")
        print("1. Manual Patient Lookup")
        print("2. Batch CSV Processing")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Step 1: Handle Manual Deductible Lookups
            manual_deductible_lookup()
            
            # Ask if user wants to continue
            continue_choice = input("\nDo you want to perform another operation? (Y/N): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("\nExiting. Thank you for using MediLink Deductible Tool!")
                break
                
        elif choice == "2":
            # Step 2: Proceed with Existing CSV Processing
            print("\n--- Starting Batch Eligibility Processing ---")
            print("Processing {} patients from CSV data...".format(len(patients)))
            
            # Ask for confirmation before starting batch processing
            confirm = input("Proceed with batch processing? (Y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Batch processing cancelled.")
                continue
            
            output_file_path = os.path.join(os.getenv('TEMP'), 'eligibility_report.txt')
            with open(output_file_path, 'w') as output_file:
                table_header = "{:<20} | {:<10} | {:<40} | {:<5} | {:<14} | {:<14}".format(
                    "Patient Name", "DOB", "Insurance Type", "PayID", "Policy Status", "Remaining Amt")
                output_file.write(table_header + "\n")
                output_file.write("-" * len(table_header) + "\n")
                print(table_header)
                print("-" * len(table_header))

                # PERFORMANCE FIX: Optimize patient-payer processing to avoid O(PxN) complexity
                # Instead of nested loops, process each patient once and try payer_ids until success
                # TODO: We should be able to determine the correct payer_id for each patient ahead of time
                # by looking up their insurance information from the CSV data or crosswalk mapping.
                # This would eliminate the need to try multiple payer_ids per patient and make this O(N).
                # CLARIFICATION: In production, use the payer_id from the CSV/crosswalk as primary.
                # Retain multi-payer probing behind a DEBUG/DIAGNOSTIC feature toggle only.
                # Suggested flag: DEBUG_MODE_PAYER_PROBE = False (module-level), default False.
                errors = []
                validation_reports = []
                processed_count = 0
                
                for dob, member_id in patients:
                    processed_count += 1
                    print("Processing patient {}/{}: Member ID {}, DOB {}".format(
                        processed_count, len(patients), member_id, dob))
                    
                    # Try each payer_id for this patient until we get a successful response
                    patient_processed = False
                    for payer_id in payer_ids:
                        try:
                            # Run with validation enabled only in debug mode
                            run_validation = DEBUG_MODE
                            eligibility_data = get_eligibility_info(client, payer_id, provider_last_name, dob, member_id, npi, run_validation=run_validation)
                            if eligibility_data is not None:
                                display_eligibility_info(eligibility_data, dob, member_id, output_file)
                                patient_processed = True
                                break  # Stop trying other payer_ids for this patient once we get a response
                        except Exception as e:
                            # Continue trying other payer_ids
                            continue
                    
                    # If no payer_id worked for this patient, log the error
                    if not patient_processed:
                        error_msg = "No successful payer_id found for patient"
                        errors.append((dob, member_id, error_msg))

                # Display errors if any
                if errors:
                    error_msg = "\nErrors encountered during API calls:\n"
                    output_file.write(error_msg)
                    print(error_msg)
                    for error in errors:
                        error_details = "DOB: {}, Member ID: {}, Error: {}\n".format(error[0], error[1], error[2])
                        output_file.write(error_details)
                        print(error_details)

            # Ask if user wants to open the report
            open_report = input("\nBatch processing complete! Open the eligibility report? (Y/N): ").strip().lower()
            if open_report in ['y', 'yes']:
                os.system('notepad.exe "{}"'.format(output_file_path))
            
            # Print summary of validation reports only in debug mode
            if DEBUG_MODE:
                print("\n" + "=" * 80)
                print("VALIDATION SUMMARY")
                print("=" * 80)
                print("Validation reports have been generated for each patient processed.")
                print("Each report compares the legacy API response with the Super Connector API response.")
                print("Check the TEMP directory for validation_report_*.txt files.")
                print("=" * 80)
            
            # Ask if user wants to continue
            continue_choice = input("\nDo you want to perform another operation? (Y/N): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("\nExiting. Thank you for using MediLink Deductible Tool!")
                break
                
        elif choice == "3":
            print("\nExiting. Thank you for using MediLink Deductible Tool!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")