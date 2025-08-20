# MediLink_ClaimStatus.py
from datetime import datetime, timedelta
import os, sys

# Import centralized logging configuration
try:
    from MediCafe.logging_config import DEBUG, PERFORMANCE_LOGGING
except ImportError:
    # Fallback to local flags if centralized config is not available
    DEBUG = False
    PERFORMANCE_LOGGING = False

# Set up project paths first
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Use core utilities for standardized imports
try:
    from MediCafe.core_utils import get_shared_config_loader, get_api_client, create_config_cache
    MediLink_ConfigLoader = get_shared_config_loader()
except ImportError:
    print("Error: Unable to import MediCafe.core_utils. Please ensure MediCafe package is properly installed.")
    sys.exit(1)

# Import api_core for claim operations
try:
    from MediCafe import api_core
except ImportError:
    api_core = None

# Calculate start_date and end_date for the API: 
# Official API documentation requires last date less than 31 days from the First Date
# Use a conservative 30-day range to stay within the 31-day limit
current_date = datetime.today()
end_date = current_date - timedelta(days=1)      # Yesterday (avoid future dates)
start_date = end_date - timedelta(days=29)       # 29 days before end date (30-day range total)

# Validate date range according to official API documentation
def validate_date_range(start_date, end_date):
    """Validate date range according to official API documentation"""
    current_date = datetime.today()
    
    if end_date > current_date:
        raise ValueError("End date cannot be in the future")
    
    date_diff = (end_date - start_date).days
    if date_diff > 30:  # Official docs say "less than 31 days"
        raise ValueError("Date range must not exceed 30 days (official API limit)")
    
    if date_diff < 0:
        raise ValueError("Start date must be before end date")
    
    # Check if dates are within reasonable range (last 24 months as per swagger)
    max_start_date = current_date - timedelta(days=730)  # 24 months
    if start_date < max_start_date:
        raise ValueError("Start date must be within last 24 months")

# Validate the calculated date range
try:
    validate_date_range(start_date, end_date)
except ValueError as e:
    print("Date validation error: {}".format(e))
    # Fallback to a safe date range within 30 days
    end_date = current_date - timedelta(days=1)
    start_date = end_date - timedelta(days=15)  # 15-day range as fallback

end_date_str = end_date.strftime('%m/%d/%Y')
start_date_str = start_date.strftime('%m/%d/%Y')

# Inline commentary: The official API documentation requires last date less than 31 days 
# from the First Date, so we use a 30-day range to stay within this limit.
if DEBUG:
    print("Using date range for API compliance (30-day range, up to yesterday)")
    print("  Start Date: {}".format(start_date_str))
    print("  End Date: {}".format(end_date_str))

# Use latest core_utils configuration cache for better performance
_get_config, (_config_cache, _crosswalk_cache) = create_config_cache()

# Load configuration using latest core_utils pattern
config, _ = _get_config()

# Get billing provider TIN from configuration
billing_provider_tin = config['MediLink_Config'].get('billing_provider_tin')

# Define the list of payer_id's to iterate over
payer_ids = ['87726', '03432', '96385', '95467', '86050', '86047', '95378', '37602']
# Allowed payer id's for UHC 87726, 03432, 96385, 95467, 86050, 86047, 95378, 37602. This api does not support payerId 06111.

# Initialize the API client via factory
client = get_api_client()
if client is None:
    if DEBUG:
        print("Warning: API client not available via factory")
    # Fallback to direct instantiation
    try:
        from MediCafe import api_core
        client = api_core.APIClient()
    except ImportError:
        print("Error: Unable to create API client")
        client = None

class ClaimCache:
    """In-memory cache for API responses"""
    def __init__(self):
        self.cache = {}  # {cache_key: {'data': response, 'payer_id': payer_id}}
    
    def get_cache_key(self, tin, start_date, end_date, payer_id):
        """Generate unique cache key for API call parameters"""
        return "{}_{}_{}_{}".format(tin, start_date, end_date, payer_id)
    
    def is_cached(self, cache_key):
        """Check if response is cached"""
        return cache_key in self.cache
    
    def get_cached_response(self, cache_key):
        """Retrieve cached response"""
        return self.cache[cache_key]['data']
    
    def cache_response(self, cache_key, response, payer_id):
        """Cache API response"""
        self.cache[cache_key] = {
            'data': response,
            'payer_id': payer_id
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()

class ConsolidatedClaims:
    """Consolidated claims data structure"""
    def __init__(self):
        self.claims_by_number = {}  # {claim_number: {claim_data, payer_sources: [payer_ids]}}
        self.payer_ids_checked = set()
        self.duplicate_warnings = []
    
    def add_claim(self, claim_data, payer_id):
        """Add claim to consolidated data, tracking payer sources"""
        claim_number = claim_data['claim_number']
        
        if claim_number not in self.claims_by_number:
            self.claims_by_number[claim_number] = {
                'data': claim_data,
                'payer_sources': [payer_id]
            }
        else:
            # Check if this is a duplicate with different data
            existing_data = self.claims_by_number[claim_number]['data']
            if self._claims_equal(existing_data, claim_data):
                # Same data, just add payer source
                if payer_id not in self.claims_by_number[claim_number]['payer_sources']:
                    self.claims_by_number[claim_number]['payer_sources'].append(payer_id)
            else:
                # Different data - create warning
                self.duplicate_warnings.append({
                    'claim_number': claim_number,
                    'existing_payers': self.claims_by_number[claim_number]['payer_sources'],
                    'new_payer': payer_id,
                    'existing_data': existing_data,
                    'new_data': claim_data
                })
        
        self.payer_ids_checked.add(payer_id)
    
    def _claims_equal(self, claim1, claim2):
        """Compare two claim data structures for equality"""
        # Compare key fields that should be identical for the same claim
        key_fields = ['claim_status', 'patient_name', 'processed_date', 'first_service_date', 
                     'total_charged_amount', 'total_allowed_amount', 'total_paid_amount', 
                     'total_patient_responsibility_amount']
        
        for field in key_fields:
            if claim1.get(field) != claim2.get(field):
                return False
        return True

def extract_claim_data(claim):
    """Extract standardized claim data from API response"""
    claim_number = claim['claimNumber']
    claim_status = claim['claimStatus']
    patient_first_name = claim['memberInfo']['ptntFn']
    patient_last_name = claim['memberInfo']['ptntLn']
    processed_date = claim['claimSummary']['processedDt']
    first_service_date = claim['claimSummary']['firstSrvcDt']
    total_charged_amount = claim['claimSummary']['totalChargedAmt']
    total_allowed_amount = claim['claimSummary']['totalAllowdAmt']
    total_paid_amount = claim['claimSummary']['totalPaidAmt']
    total_patient_responsibility_amount = claim['claimSummary']['totalPtntRespAmt']
    
    patient_name = "{} {}".format(patient_first_name, patient_last_name)
    
    return {
        'claim_number': claim_number,
        'claim_status': claim_status,
        'patient_name': patient_name,
        'processed_date': processed_date,
        'first_service_date': first_service_date,
        'total_charged_amount': total_charged_amount,
        'total_allowed_amount': total_allowed_amount,
        'total_paid_amount': total_paid_amount,
        'total_patient_responsibility_amount': total_patient_responsibility_amount,
        'claim_xwalk_data': claim['claimSummary']['clmXWalkData']
    }

def handle_api_error(error, payer_id):
    """Handle specific API errors according to official documentation"""
    error_message = str(error)
    
    # Handle specific error codes from official documentation
    if "LCLM_PS_102" in error_message:
        return "Mandatory element missing in request (tin, firstServiceDt, lastServiceDt, or payerId)"
    elif "LCLM_PS_105" in error_message or "LCLM_PS_202" in error_message:
        return "Authorization error: Payer ID {} not allowed".format(payer_id)
    elif "LCLM_PS_106" in error_message:
        return "Invalid parameter combination: must use (firstServiceDt,lastServiceDt) or (transactionId)"
    elif "LCLM_PS_107" in error_message:
        return "Date range must be within last 24 months"
    elif "LCLM_PS_108" in error_message or "LCLM_PS_111" in error_message:
        return "Incorrect date format: use MM/dd/yyyy"
    elif "LCLM_PS_112" in error_message:
        return "Date range exceeds 30 days limit (official API constraint)"
    elif "LCLM_PS_201" in error_message:
        return "No data found with given request parameters"
    elif "LCLM_PS_306" in error_message:
        return "Search exceeds 500 claims limit - narrow date range"
    elif "LCLM_PS_500" in error_message:
        return "Server error: Exception from Claims 360 - try again later"
    elif "401" in error_message:
        return "Authentication error: check credentials"
    elif "403" in error_message:
        return "Authorization error: insufficient permissions"
    elif "500" in error_message:
        return "Server error: internal system failure"
    else:
        return "Unknown error: {}".format(error_message)

def process_claims_with_payer_rotation(billing_provider_tin, start_date_str, end_date_str, 
                                     payer_ids, cache, consolidated_claims):
    """
    Process claims across multiple payer IDs with caching and consolidation
    """
    from MediCafe.core_utils import get_api_client
    client = get_api_client()
    if client is None:
        if DEBUG:
            print("Warning: API client not available via factory")
        # Fallback to direct instantiation
        try:
            from MediCafe import api_core
            client = api_core.APIClient()
        except ImportError:
            print("Error: Unable to create API client")
            return
    
    for payer_id in payer_ids:
        if DEBUG:
            print("Processing Payer ID: {}".format(payer_id))
        
        # Generate cache key
        cache_key = cache.get_cache_key(billing_provider_tin, start_date_str, end_date_str, payer_id)
        
        # Check cache first
        if cache.is_cached(cache_key):
            if DEBUG:
                print("  Using cached response for Payer ID: {}".format(payer_id))
            claim_summary = cache.get_cached_response(cache_key)
        else:
            if DEBUG:
                print("  Making API call for Payer ID: {}".format(payer_id))
            try:
                # Import api_core locally to ensure it's available
                from MediCafe import api_core
                claim_summary = api_core.get_claim_summary_by_provider(
                    client, billing_provider_tin, start_date_str, end_date_str, 
                    payer_id=payer_id
                )
                cache.cache_response(cache_key, claim_summary, payer_id)
            except Exception as e:
                error_msg = handle_api_error(e, payer_id)
                print("  Error processing Payer ID {}: {}".format(payer_id, error_msg))
                
                # Log the error for debugging (file only, not console)
                MediLink_ConfigLoader.log(
                    "API Error for Payer ID {}: {}".format(payer_id, error_msg),
                    level="ERROR",
                    console_output=False
                )
                continue
        
        # Process claims from this payer
        claims = claim_summary.get('claims', [])
        for claim in claims:
            claim_data = extract_claim_data(claim)
            consolidated_claims.add_claim(claim_data, payer_id)

def display_consolidated_claims(consolidated_claims, output_file):
    """
    Display consolidated claims with payer ID header and duplicate warnings
    """
    # Display header with all payer IDs checked
    payer_ids_str = ", ".join(sorted(consolidated_claims.payer_ids_checked))
    header = "Payer IDs Checked: {} | Start Date: {} | End Date: {}".format(
        payer_ids_str, start_date_str, end_date_str)
    print(header)
    output_file.write(header + "\n")
    print("=" * len(header))
    output_file.write("=" * len(header) + "\n")
    
    # Table header
    table_header = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7} | {:<15}".format(
        "Claim #", "Status", "Patient", "Proc.", "Serv.", "Allowed", "Paid", "Pt Resp", "Charged", "Payer Sources")
    print(table_header)
    output_file.write(table_header + "\n")
    print("-" * len(table_header))
    output_file.write("-" * len(table_header) + "\n")
    
    # Sort claims by first service date
    sorted_claims = sorted(
        consolidated_claims.claims_by_number.items(),
        key=lambda x: x[1]['data']['first_service_date']
    )
    
    # Display each claim
    for claim_number, claim_info in sorted_claims:
        claim_data = claim_info['data']
        payer_sources = claim_info['payer_sources']
        
        # Format payer sources
        payer_sources_str = ", ".join(sorted(payer_sources))
        
        table_row = "{:<10} | {:<10} | {:<20} | {:<6} | {:<6} | {:<7} | {:<7} | {:<7} | {:<7} | {:<15}".format(
            claim_number, claim_data['claim_status'], claim_data['patient_name'][:20],
            claim_data['processed_date'][:5], claim_data['first_service_date'][:5],
            claim_data['total_allowed_amount'], claim_data['total_paid_amount'],
            claim_data['total_patient_responsibility_amount'], claim_data['total_charged_amount'],
            payer_sources_str
        )
        print(table_row)
        output_file.write(table_row + "\n")
        
        # Display crosswalk data for $0.00 claims
        if claim_data['total_paid_amount'] == '0.00':
            for xwalk in claim_data['claim_xwalk_data']:
                clm507Cd = xwalk['clm507Cd']
                clm507CdDesc = xwalk['clm507CdDesc']
                clm508Cd = xwalk['clm508Cd']
                clm508CdDesc = xwalk['clm508CdDesc']
                clmIcnSufxCd = xwalk['clmIcnSufxCd']
                if DEBUG:
                    print("  507: {} ({}) | 508: {} ({}) | ICN Suffix: {}".format(
                        clm507Cd, clm507CdDesc, clm508Cd, clm508CdDesc, clmIcnSufxCd))
    
    # Display duplicate warnings (terminal and log only, not file)
    if consolidated_claims.duplicate_warnings:
        if DEBUG:
            print("\n" + "="*80)
            print("DUPLICATE CLAIM WARNINGS:")
            print("="*80)
        
        for warning in consolidated_claims.duplicate_warnings:
            warning_msg = (
                "Claim {} found in multiple payers with different data:\n"
                "  Existing payers: {}\n"
                "  New payer: {}\n"
                "  Status difference: {} vs {}\n"
                "  Amount difference: ${} vs ${}".format(
                    warning['claim_number'],
                    ", ".join(warning['existing_payers']),
                    warning['new_payer'],
                    warning['existing_data']['claim_status'],
                    warning['new_data']['claim_status'],
                    warning['existing_data']['total_paid_amount'],
                    warning['new_data']['total_paid_amount']
                )
            )
            if DEBUG:
                print(warning_msg)
            
            # Log the warning (file only, not console)
            MediLink_ConfigLoader.log(
                "Duplicate claim warning: {}".format(warning_msg),
                level="WARNING",
                console_output=False
            )

# Initialize cache and consolidated claims
cache = ClaimCache()
consolidated_claims = ConsolidatedClaims()

# Process claims with payer rotation
process_claims_with_payer_rotation(
    billing_provider_tin, start_date_str, end_date_str, payer_ids, cache, consolidated_claims
)

# Display consolidated results
temp_dir = os.getenv('TEMP') or os.getenv('TMP') or '/tmp'  # Cross-platform temp directory
output_file_path = os.path.join(temp_dir, 'claim_summary_report.txt')
with open(output_file_path, 'w') as output_file:
    display_consolidated_claims(consolidated_claims, output_file)

# Clear cache after consolidated table is generated
cache.clear_cache()

# Open the generated file (cross-platform approach)
try:
    if os.name == 'nt':  # Windows
        os.startfile(output_file_path)
    elif os.name == 'posix':  # Unix/Linux/MacOS
        import subprocess
        subprocess.call(['xdg-open', output_file_path])
    else:
        if DEBUG:
            print("File saved to: {}".format(output_file_path))
except Exception as e:
    if DEBUG:
        print("File saved to: {}".format(output_file_path))
        print("Could not open file automatically: {}".format(e))