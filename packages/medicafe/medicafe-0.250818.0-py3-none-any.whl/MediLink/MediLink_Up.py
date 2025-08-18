# MediLink_Up.py
"""
Notes:
- Duplicate detection relies on a JSONL index under MediLink_Config['receiptsRoot'].
  If 'receiptsRoot' is missing, duplicate checks are skipped with no errors.
- The claim_key used for deconfliction is practical rather than cryptographic:
  it combines (patient_id if available, else ''), (payer_id or primary_insurance), DOS, and a simple service/procedure indicator.
  In this file-level flow, we approximate with primary_insurance + DOS + file basename for pre-checks.
  Upstream detection now also flags duplicates per patient record using procedure code when available.
- We do NOT write to the index until a successful submission occurs.
- All I/O uses ASCII-safe defaults.
"""
from datetime import datetime
import os, re, subprocess, traceback
try:
    from tqdm import tqdm
except ImportError:
    # Fallback for when tqdm is not available
    def tqdm(iterable, **kwargs):
        return iterable
import MediLink_837p_encoder
from MediLink_DataMgmt import operate_winscp

# Use core utilities for standardized imports
from MediCafe.core_utils import get_shared_config_loader, get_api_client
MediLink_ConfigLoader = get_shared_config_loader()
log = MediLink_ConfigLoader.log
load_configuration = MediLink_ConfigLoader.load_configuration

# Import api_core for claim submission
try:
    from MediCafe import api_core
except ImportError:
    api_core = None

# Import submission index helpers (XP-safe JSONL)
try:
    from MediCafe.submission_index import (
        compute_claim_key,
        find_by_claim_key,
        append_submission_record
    )
except Exception:
    compute_claim_key = None
    find_by_claim_key = None
    append_submission_record = None

# Pre-compile regex patterns for better performance
GS_PATTERN = re.compile(r'GS\*HC\*[^*]*\*[^*]*\*([0-9]{8})\*([0-9]{4})')
SE_PATTERN = re.compile(r'SE\*\d+\*\d{4}~')
NM1_IL_PATTERN = re.compile(r'NM1\*IL\*1\*([^*]+)\*([^*]+)\*([^*]*)')
DTP_472_PATTERN = re.compile(r'DTP\*472\D*8\*([0-9]{8})')
CLM_PATTERN = re.compile(r'CLM\*[^\*]*\*([0-9]+\.?[0-9]*)')
NM1_PR_PATTERN = re.compile(r'NM1\*PR\*2\*([^*]+)\*')

# Internet Connectivity Check
def check_internet_connection():
    """
    Checks if there is an active internet connection.
    Returns: Boolean indicating internet connectivity status.
    """
    # Check if TestMode is enabled
    config, _ = load_configuration()
    if config.get("MediLink_Config", {}).get("TestMode", True):
        # If TestMode is True, skip the connectivity check and return True as if the internet connection were fine
        return True
        
    try:
        # Run a ping command to a reliable external server (e.g., Google's DNS server)
        ping_process = subprocess.Popen(["ping", "-n", "1", "8.8.8.8"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_output, ping_error = ping_process.communicate()

        # Check if the ping was successful
        if "Reply from" in ping_output.decode("utf-8"):
            return True
        else:
            return False
    except Exception as e:
        print("An error occurred checking for internet connectivity:", e)
        return False

def submit_claims(detailed_patient_data_grouped_by_endpoint, config, crosswalk):
    """
    Submits claims for each endpoint, either via WinSCP or API, based on configuration settings.

    Deconfliction (XP-safe):
    - If JSONL index helpers are available and receiptsRoot is configured, compute a claim_key per 837p file
      and skip submit if index already contains that key (duplicate protection).
    - After a successful submission, append an index record.
    """
    # Normalize configuration for safe nested access
    if not isinstance(config, dict):
        try:
            config, _ = load_configuration()
        except Exception:
            config = {}
    if isinstance(config, dict):
        cfg_candidate = config.get('MediLink_Config')
        if isinstance(cfg_candidate, dict):
            cfg = cfg_candidate
        else:
            cfg = config
    else:
        cfg = {}

    # Resolve receipts folder for index (use same path as receipts)
    receipts_root = cfg.get('local_claims_path', None)

    # Accumulate submission results
    submission_results = {}
    
    if not detailed_patient_data_grouped_by_endpoint:
        print("No new files detected for submission.")
        return

    # Iterate through each endpoint and submit claims
    for endpoint, patients_data in tqdm(detailed_patient_data_grouped_by_endpoint.items(), desc="Progress", unit="endpoint"):
        # Debug context to trace NoneType.get issues early
        try:
            log("[submit_claims] Starting endpoint: {}".format(endpoint), level="INFO")
            if patients_data is None:
                log("[submit_claims] Warning: patients_data is None for endpoint {}".format(endpoint), level="WARNING")
            else:
                try:
                    log("[submit_claims] patients_data count: {}".format(len(patients_data)), level="DEBUG")
                except Exception:
                    log("[submit_claims] patients_data length unavailable (type: {})".format(type(patients_data)), level="DEBUG")
        except Exception:
            pass

        if not patients_data:
            continue

        # Determine the submission method (e.g., "winscp" or "api")
        try:
            method = cfg.get('endpoints', {}).get(endpoint, {}).get('submission_method', 'winscp')
        except Exception as e:
            log("[submit_claims] Error deriving submission method for endpoint {}: {}".format(endpoint, e), level="ERROR")
            method = 'winscp'

        if True: #confirm_transmission({endpoint: patients_data}): # Confirm transmission to each endpoint with detailed overview
            if check_internet_connection():
                client = get_api_client()
                if client is None:
                    print("Warning: API client not available via factory")
                    # Fallback to direct instantiation  
                    try:
                        from MediCafe import api_core
                        client = api_core.APIClient()
                    except ImportError:
                        print("Error: Unable to create API client")
                        continue
                # Process files per endpoint
                try:
                    # Sanitize patient data structure before conversion
                    safe_patients = []
                    if isinstance(patients_data, list):
                        safe_patients = [item for item in patients_data if isinstance(item, dict)]
                    elif isinstance(patients_data, dict):
                        safe_patients = [patients_data]
                    else:
                        log("[submit_claims] Unexpected patients_data type for {}: {}".format(endpoint, type(patients_data)), level="ERROR")
                        safe_patients = []

                    converted_files = MediLink_837p_encoder.convert_files_for_submission(safe_patients, config, crosswalk, client)
                except Exception as e:
                    tb = traceback.format_exc()
                    # Log via logger (may fail if logger expects config); also print to stderr to guarantee visibility
                    try:
                        log("[submit_claims] convert_files_for_submission failed for endpoint {}: {}\nTraceback: {}".format(endpoint, e, tb), level="ERROR")
                    except Exception:
                        pass
                    try:
                        import sys as _sys
                        _sys.stderr.write("[submit_claims] convert_files_for_submission failed for endpoint {}: {}\n".format(endpoint, e))
                        _sys.stderr.write(tb + "\n")
                    except Exception:
                        pass
                    raise
                if converted_files:
                    # Deconfliction pre-check per file if helpers available
                    filtered_files = []
                    for file_path in converted_files:
                        if compute_claim_key and find_by_claim_key and receipts_root:
                            try:
                                # Compute a simple service hash from file path (can be improved later)
                                service_hash = os.path.basename(file_path)
                                # Attempt to parse minimal patient_id and DOS from filename if available
                                # For now, rely on patient data embedded in file content via parse_837p_file
                                patients, _ = parse_837p_file(file_path)
                                # If we cannot compute a stable key, skip deconflict
                                if patients:
                                    # Use first patient for keying; future improvement: per-service keys
                                    p = patients[0]
                                    patient_id = ""  # unknown at this stage (facesheet may not contain chart)
                                    payer_id = ""
                                    primary_insurance = p.get('insurance_name', '')
                                    dos = p.get('service_date', '')
                                    claim_key = compute_claim_key(patient_id, payer_id, primary_insurance, dos, service_hash)
                                    existing = find_by_claim_key(receipts_root, claim_key)
                                    if existing:
                                        print("Duplicate detected; skipping file: {}".format(file_path))
                                        continue
                            except Exception:
                                # Fail open (do not block submission)
                                pass
                        filtered_files.append(file_path)

                    if not filtered_files:
                        print("All files skipped as duplicates for endpoint {}.".format(endpoint))
                        submission_results[endpoint] = {}
                    elif method == 'winscp':
                        # Transmit files via WinSCP
                        try:
                            operation_type = "upload"
                            endpoint_cfg = cfg.get('endpoints', {}).get(endpoint, {})
                            local_claims_path = cfg.get('local_claims_path', '.')
                            transmission_result = operate_winscp(operation_type, filtered_files, endpoint_cfg, local_claims_path, config)
                            success_dict = handle_transmission_result(transmission_result, config, operation_type, method)
                            submission_results[endpoint] = success_dict
                        except FileNotFoundError as e:
                            print("Failed to transmit files to {}. Error: Log file not found - {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": "Log file not found - " + str(e)}
                        except IOError as e:
                            print("Failed to transmit files to {}. Error: Input/output error - {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": "Input/output error - " + str(e)}
                        except Exception as e:
                            print("Failed to transmit files to {}. Error: {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": str(e)}
                    elif method == 'api':
                        # Transmit files via API
                        try:
                            api_responses = []
                            for file_path in filtered_files:
                                with open(file_path, 'r') as file:
                                    # Optimize string operations by doing replacements in one pass
                                    x12_request_data = file.read().replace('\n', '').replace('\r', '').strip()
                                    try:
                                        from MediCafe import api_core
                                        response = api_core.submit_uhc_claim(client, x12_request_data)
                                    except ImportError:
                                        print("Error: Unable to import api_core for claim submission")
                                        response = {"error": "API module not available"}
                                    api_responses.append((file_path, response))
                            success_dict = handle_transmission_result(api_responses, config, "api", method)
                            submission_results[endpoint] = success_dict
                        except Exception as e:
                            print("Failed to transmit files via API to {}. Error: {}".format(endpoint, str(e)))
                            submission_results[endpoint] = {"status": False, "error": str(e)}
                else:
                    print("No files were converted for transmission to {}.".format(endpoint))
            else:
                print("Error: No internet connection detected.")
                log("Error: No internet connection detected.", level="ERROR")
                try_again = input("Do you want to try again? (Y/N): ").strip().lower()
                if try_again != 'y':
                    print("Exiting transmission process. Please try again later.")
                    return  # Exiting the function if the user decides not to retry
        else:
            # This else statement is inaccessible because it is preceded by an if True condition, 
            # which is always true and effectively makes the else clause unreachable.
            # To handle this, we need to decide under what conditions the submission should be canceled. 
            # One option is to replace the if True with a condition that checks for some pre-submission criteria. 
            # For instance, if there is a confirmation step or additional checks that need to be performed before 
            # proceeding with the submission, these could be included here.
            print("Transmission canceled for endpoint {}.".format(endpoint)) 
        
        # Continue to next endpoint regardless of the previous outcomes

    # Build and display receipt
    build_and_display_receipt(submission_results, config)

    # Append index records for successes
    try:
        if append_submission_record and isinstance(submission_results, dict):
            # Resolve receipts root
            if isinstance(config, dict):
                _cfg2 = config.get('MediLink_Config')
                cfg2 = _cfg2 if isinstance(_cfg2, dict) else config
            else:
                cfg2 = {}
            receipts_root2 = cfg2.get('local_claims_path', None)
            if receipts_root2:
                for endpoint, files in submission_results.items():
                    for file_path, result in files.items():
                        try:
                            status, message = result
                            if status:
                                patients, submitted_at = parse_837p_file(file_path)
                                # Take first patient for keying; improve later for per-service handling
                                p = patients[0] if patients else {}
                                claim_key = compute_claim_key("", "", p.get('insurance_name', ''), p.get('service_date', ''), os.path.basename(file_path))
                                record = {
                                    'claim_key': claim_key,
                                    'patient_id': "",
                                    'payer_id': "",
                                    'primary_insurance': p.get('insurance_name', ''),
                                    'dos': p.get('service_date', ''),
                                    'endpoint': endpoint,
                                    'submitted_at': submitted_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'receipt_file': os.path.basename(file_path),
                                    'status': 'success'
                                }
                                append_submission_record(receipts_root2, record)
                        except Exception:
                            continue
    except Exception:
        pass
    
    print("Claim submission process completed.\n")

def handle_transmission_result(transmission_result, config, operation_type, method):
    """
    Analyze the outcomes of file transmissions based on WinSCP log entries or API responses.

    Parameters:
    - transmission_result: List of paths for files that were attempted to be transmitted or API response details.
    - config: Configuration dictionary containing paths and settings.
    - operation_type: The type of operation being performed (e.g., "upload").
    - method: The transmission method used ("winscp" or "api").

    Returns:
    - Dictionary mapping each file path or API response to a tuple indicating successful transmission and any relevant messages.
    """
    success_dict = {}

    if method == "winscp":
        # Define the log filename based on the operation type
        log_filename = "winscp_{}.log".format(operation_type)
        # XP/WinSCP NOTE:
        # - Historically this used 'local_claims_path' which is typically the UPLOAD staging directory.
        # - On some XP setups, WinSCP writes logs to a different directory than where files are uploaded or downloaded.
        # - To avoid brittle assumptions, allow an explicit 'winscp_log_dir' override while preserving legacy default.
        # - Fallback remains 'local_claims_path' to preserve current behavior.
        # Ensure cfg is a dict for safe access
        if isinstance(config, dict):
            _cfg_candidate = config.get('MediLink_Config')
            if isinstance(_cfg_candidate, dict):
                cfg = _cfg_candidate
            else:
                cfg = config
        else:
            cfg = {}
        winscp_log_dir = (
            cfg.get('winscp_log_dir')
            or cfg.get('local_claims_path')
            or '.'
        )
        # If you observe missing logs, verify WinSCP's real log location in the ini or via command-line switches.
        # Consider adding a scheduled cleanup (daily) to prevent unbounded log growth on XP machines.
        log_path = os.path.join(winscp_log_dir, log_filename)
        
        try:
            # Read the contents of the WinSCP log file
            with open(log_path, 'r') as log_file:
                log_contents = log_file.readlines()

            if not log_contents:
                # Handle the case where the log file is empty
                log("Log file '{}' is empty.".format(log_path))
                success_dict = {file_path: (False, "Log file empty") for file_path in transmission_result}
            else:
                # Process the last few lines of the log file for transfer status
                last_lines = log_contents[-35:]
                for file_path in transmission_result:
                    # Pre-format success messages to avoid repeated string formatting
                    success_message = "Transfer done: '{}'".format(file_path)
                    additional_success_message = "Upload of file '{}' was successful, but error occurred while setting the permissions and/or timestamp.".format(file_path)
                    # Use any() with generator expression for better performance
                    success = any(success_message in line or additional_success_message in line for line in last_lines)
                    message = "Success" if success else "Transfer incomplete or error occurred"
                    success_dict[file_path] = (success, message)

        except FileNotFoundError:
            # Log file not found, handle the error
            log("Log file '{}' not found.".format(log_path))
            success_dict = {file_path: (False, "Log file not found") for file_path in transmission_result}
        except IOError as e:
            # Handle IO errors, such as issues reading the log file
            log("IO error when handling the log file '{}': {}".format(log_path, e))
            success_dict = {file_path: (False, "IO error: {}".format(e)) for file_path in transmission_result}
        except Exception as e:
            # Catch all other exceptions and log them
            log("Error processing the transmission log: {}".format(e))
            success_dict = {file_path: (False, "Error: {}".format(e)) for file_path in transmission_result}

    elif method == "api":
        # Process each API response to determine the success status
        for file_path, response in transmission_result:
            try:
                # Handle responses that may be None or non-dict safely
                if isinstance(response, dict):
                    message = response.get('message', 'No message provided')
                    success = message in [
                        "Claim validated and sent for further processing",
                        "Acknowledgement pending"
                    ]
                else:
                    message = str(response) if response is not None else 'No response received'
                    success = False
                success_dict[file_path] = (success, message)
            except Exception as e:
                # Handle API exception
                log("Error processing API response: {}".format(e))
                success_dict[file_path] = (False, str(e))

    return success_dict

def build_and_display_receipt(submission_results, config):
    """
    Builds and displays a receipt for submitted claims, including both successful and failed submissions.
    A receipt of submitted claims is typically attached to each printed facesheet for recordkeeping confirming submission.
    
    Parameters:
    - submission_results: Dictionary containing submission results with detailed information for each endpoint.
    - config: Configuration settings loaded from a JSON file.

    Returns:
    - None
    """
    # Prepare data for receipt
    receipt_data = prepare_receipt_data(submission_results)

    # Build the receipt
    receipt_content = build_receipt_content(receipt_data)

    # Print the receipt to the screen
    log("Printing receipt...")
    print(receipt_content)

    # Save the receipt to a text file
    save_receipt_to_file(receipt_content, config)

    log("Receipt has been generated and saved.")

def prepare_receipt_data(submission_results):
    """
    Prepare submission results for a receipt, including data from both successful and failed submissions.

    This function extracts patient names, dates of service, amounts billed, and insurance names from an 837p file.
    It also includes the date and time of batch claim submission, and the receiver name from the 1000B segment.
    Data is organized by receiver name and includes both successful and failed submissions.

    Parameters:
    - submission_results (dict): Contains submission results grouped by endpoint, with detailed status information.

    Returns:
    - dict: Organized data for receipt preparation, including both successful and failed submission details.
    """
    receipt_data = {}
    for endpoint, files in submission_results.items():
        log("Processing endpoint: {}".format(endpoint), level="INFO")
        for file_path, file_result in files.items():
            log("File path: {}".format(file_path), level="DEBUG")
            log("File result: {}".format(file_result), level="DEBUG")

            try:
                # Unpack the tuple to get status and message
                status, message = file_result
            except ValueError as e:
                file_result_length = len(file_result) if hasattr(file_result, '__len__') else 'Unknown'
                error_msg = 'Too many values to unpack.' if 'too many values to unpack' in str(e) else \
                            'Not enough values to unpack.' if 'not enough values to unpack' in str(e) else \
                            'Value unpacking error.'
                log("ValueError: {} for file_result: {} (Length: {})".format(error_msg, file_result, file_result_length), level="ERROR")
                continue
            except Exception as e:
                tb = traceback.format_exc()
                log("Unexpected error: {}. Traceback: {}".format(e, tb), level="ERROR")
                continue

            log("Status: {}, Message: {}".format(status, message), level="DEBUG")

            if endpoint not in receipt_data:
                receipt_data[endpoint] = {
                    "patients": [],
                    "date_of_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

            # Parse patient details and add the result status and message
            patient_data, _ = parse_837p_file(file_path)
            for patient in patient_data:
                patient['status'] = status
                patient['message'] = message

            receipt_data[endpoint]["patients"].extend(patient_data)
    
    validate_data(receipt_data)
    log("Receipt data: {}".format(receipt_data), level="DEBUG")
    
    return receipt_data

def validate_data(receipt_data):
    # Simple validation to check if data fields are correctly populated
    for endpoint, data in receipt_data.items():
        patients = data.get("patients", [])
        for index, patient in enumerate(patients, start=1):
            missing_fields = [field for field in ('name', 'service_date', 'amount_billed', 'insurance_name', 'status') if patient.get(field) in (None, '')]
            
            if missing_fields:
                # Log the missing fields without revealing PHI
                log("Receipt Data validation error for endpoint '{}', patient {}: Missing information in fields: {}".format(endpoint, index, ", ".join(missing_fields)))
    return True

def parse_837p_file(file_path):
    """
    Parse an 837p file to extract patient details and date of submission.

    This function reads the specified 837p file, extracts patient details such as name, service date, and amount billed,
    and retrieves the date of submission from the GS segment. It then organizes this information into a list of dictionaries
    containing patient data. If the GS segment is not found, it falls back to using the current date and time.

    Parameters:
    - file_path (str): The path to the 837p file to parse.

    Returns:
    - tuple: A tuple containing two elements:
        - A list of dictionaries, where each dictionary represents patient details including name, service date, and amount billed.
        - A string representing the date and time of submission in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    patient_details = []
    date_of_submission = None
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            log("Parsing submitted 837p...")

            # Extract the submission date from the GS segment
            gs_match = GS_PATTERN.search(content)
            if gs_match:
                date = gs_match.group(1)
                time = gs_match.group(2)
                date_of_submission = datetime.strptime("{}{}".format(date, time), "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Fallback to the current date and time if GS segment is not found
                date_of_submission = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Split content using 'SE*{count}*{control_number}~' as delimiter
            patient_records = SE_PATTERN.split(content)
            
            # Remove any empty strings from list that may have been added from split
            patient_records = [record for record in patient_records if record.strip()]
            
            for record in patient_records:
                # Extract patient name
                name_match = NM1_IL_PATTERN.search(record)
                # Extract service date
                service_date_match = DTP_472_PATTERN.search(record)
                # Extract claim amount
                amount_match = CLM_PATTERN.search(record)
                # Extract insurance name (payer_name)
                insurance_name_match = NM1_PR_PATTERN.search(record)
                
                if name_match and service_date_match and amount_match:
                    # Handle optional middle name
                    middle_name = name_match.group(3).strip() if name_match.group(3) else ""
                    patient_name = "{} {} {}".format(name_match.group(2), middle_name, name_match.group(1)).strip()
                    
                    # Optimize date formatting
                    service_date_raw = service_date_match.group(1)
                    service_date = "{}-{}-{}".format(service_date_raw[:4], service_date_raw[4:6], service_date_raw[6:])
                    
                    amount_billed = float(amount_match.group(1))
                    insurance_name = insurance_name_match.group(1) if insurance_name_match else ""
                    
                    patient_details.append({
                        "name": patient_name,
                        "service_date": service_date,
                        "amount_billed": amount_billed,
                        "insurance_name": insurance_name
                    })
    except Exception as e:
        print("Error reading or parsing the 837p file: {0}".format(str(e)))
    
    return patient_details, date_of_submission

def build_receipt_content(receipt_data):
    """
    Build the receipt content in a human-readable ASCII format with a tabular data presentation for patient information.

    Args:
        receipt_data (dict): Dictionary containing receipt data with patient details.

    Returns:
        str: Formatted receipt content as a string.
    """
    # Build the receipt content in a human-readable ASCII format
    receipt_lines = ["Submission Receipt", "=" * 60, ""]  # Header

    for endpoint, data in receipt_data.items():
        header = "Endpoint: {0} (Submitted: {1})".format(endpoint, data['date_of_submission'])
        receipt_lines.extend([header, "-" * len(header)])
        
        # Table headers
        table_header = "{:<20} | {:<15} | {:<15} | {:<20} | {:<10}".format("Patient", "Service Date", "Amount Billed", "Insurance", "Status")
        receipt_lines.append(table_header)
        receipt_lines.append("-" * len(table_header))
        
        # Pre-format the status display to avoid repeated conditional checks
        for patient in data["patients"]:
            status_display = "SUCCESS" if patient['status'] else patient['message']
            # Use join for better performance than multiple format calls
            patient_info = " | ".join([
                "{:<20}".format(patient['name']),
                "{:<15}".format(patient['service_date']),
                "${:<14}".format(patient['amount_billed']),
                "{:<20}".format(patient['insurance_name']),
                "{:<10}".format(status_display)
            ])
            receipt_lines.append(patient_info)
        
        receipt_lines.append("")  # Blank line for separation
    
    receipt_content = "\n".join(receipt_lines)
    return receipt_content

def save_receipt_to_file(receipt_content, config):
    """
    Saves the receipt content to a text file and opens it for the user.

    Parameters:
    - receipt_content (str): The formatted content of the receipt.
    - config: Configuration settings loaded from a JSON file.

    Returns:
    - None
    """
    try:
        file_name = "Receipt_{0}.txt".format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        # Ensure cfg is a dict for safe path resolution
        if isinstance(config, dict):
            cfg_candidate = config.get('MediLink_Config')
            if isinstance(cfg_candidate, dict):
                cfg = cfg_candidate
            else:
                cfg = config
        else:
            cfg = {}
        file_path = os.path.join(cfg.get('local_claims_path', '.'), file_name)
        
        with open(file_path, 'w') as file:
            file.write(receipt_content)
        
        log("Receipt saved to:", file_path)
        # Open the file automatically for the user (Windows-specific)
        if os.name == 'nt':
            os.startfile(file_path)
    except Exception as e:
        print("Failed to save or open receipt file:", e)

# Secure File Transmission
def confirm_transmission(detailed_patient_data_grouped_by_endpoint):
    """
    Displays detailed patient data ready for transmission and their endpoints, 
    asking for user confirmation before proceeding.

    :param detailed_patient_data_grouped_by_endpoint: Dictionary with endpoints as keys and 
            lists of detailed patient data as values.
    :param config: Configuration settings loaded from a JSON file.
    """ 
    # Clear terminal for clarity
    os.system('cls')
    
    print("\nReview of patient data ready for transmission:")
    for endpoint, patient_data_list in detailed_patient_data_grouped_by_endpoint.items():
        print("\nEndpoint: {0}".format(endpoint))
        for patient_data in patient_data_list:
            patient_info = "({1}) {0}".format(patient_data['patient_name'], patient_data['patient_id'])
            print("- {:<33} | {:<5}, ${:<6}, {}".format(
                patient_info, patient_data['surgery_date'][:5], patient_data['amount'], patient_data['primary_insurance']))
    
    while True:
        confirmation = input("\nProceed with transmission to all endpoints? (Y/N): ").strip().lower()
        if confirmation in ['y', 'n']:
            return confirmation == 'y'
        else:
            print("Invalid input. Please enter 'Y' for yes or 'N' for no.")

# Entry point if this script is run directly. Probably needs to be handled better.
if __name__ == "__main__":
    print("Please run MediLink directly.")