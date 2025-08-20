# MediLink_Display_Utils.py
# Display utility functions extracted from MediLink_UI.py to eliminate circular dependencies
# Provides centralized display functions for insurance options and patient summaries

from datetime import datetime

# Use core utilities for standardized imports
from MediCafe.core_utils import get_shared_config_loader, extract_medilink_config
MediLink_ConfigLoader = get_shared_config_loader()

def display_insurance_options(insurance_options=None):
    """Display insurance options, loading from config if not provided"""
    
    if insurance_options is None:
        config, _ = MediLink_ConfigLoader.load_configuration()
        medi = extract_medilink_config(config)
        insurance_options = medi.get('insurance_options', {})
    
    print("\nInsurance Type Options (SBR09 Codes):")
    print("-" * 50)
    for code, description in sorted(insurance_options.items()):
        print("{:>3}: {}".format(code, description))
    print("-" * 50)
    print("Note: '12' (PPO) is the default if no selection is made.")
    print()  # Add a blank line for better readability

def display_patient_summaries(detailed_patient_data):
    """
    Displays summaries of all patients and their suggested endpoints.
    """
    print("\nSummary of patient details and suggested endpoint:")
    
    # Sort by insurance_type_source priority for clearer grouping
    priority = {'API': 0, 'MANUAL': 1, 'DEFAULT': 2, 'DEFAULT_FALLBACK': 2}
    def sort_key(item):
        src = item.get('insurance_type_source', '')
        return (priority.get(src, 2), item.get('surgery_date', ''), item.get('patient_name', ''))
    sorted_data = sorted(detailed_patient_data, key=sort_key)

    for index, summary in enumerate(sorted_data, start=1):
        try:
            display_file_summary(index, summary)
        except KeyError as e:
            print("Summary at index {} is missing key: {}".format(index, e))
    print() # add blank line for improved readability.
    print("Legend: Src=API (auto), MAN (manual), DEF (default) | [DUP] indicates a previously submitted matching claim")

def display_file_summary(index, summary):
    # Ensure surgery_date is converted to a datetime object
    surgery_date = datetime.strptime(summary['surgery_date'], "%m-%d-%y")
    
    # Add header row if it's the first index
    if index == 1:
        print("{:<3} {:5} {:<10} {:<20} {:<15} {:<3} {:<5} {:<8} {:<20}".format(
            "No.", "Date", "ID", "Name", "Primary Ins.", "IT", "Src", "Flag", "Current Endpoint"
        ))
        print("-"*100)

    # Check if insurance_type is available; if not, set a default placeholder (this should already be '12' at this point)
    insurance_type = summary.get('insurance_type', '--')
    insurance_source = summary.get('insurance_type_source', '')
    duplicate_flag = '[DUP]' if summary.get('duplicate_candidate') else ''
    
    # Get the effective endpoint (confirmed > user preference > suggestion > default)
    effective_endpoint = (summary.get('confirmed_endpoint') or 
                         summary.get('user_preferred_endpoint') or 
                         summary.get('suggested_endpoint', 'AVAILITY'))

    # Format insurance type for display - handle both 2 and 3 character codes
    if insurance_type and len(insurance_type) <= 3:
        insurance_display = insurance_type
    else:
        insurance_display = insurance_type[:3] if insurance_type else '--'

    # Shorten source for compact display
    if insurance_source in ['DEFAULT_FALLBACK', 'DEFAULT']:
        source_display = 'DEF'
    elif insurance_source == 'MANUAL':
        source_display = 'MAN'
    elif insurance_source == 'API':
        source_display = 'API'
    else:
        source_display = ''

    print("{:02d}. {:5} ({:<8}) {:<20} {:<15} {:<3} {:<5} {:<8} {:<20}".format(
        index,
        surgery_date.strftime("%m-%d"),
        summary['patient_id'],
        summary['patient_name'][:20],
        summary['primary_insurance'][:15],
        insurance_display,
        source_display,
        duplicate_flag,
        effective_endpoint[:20])
    ) 