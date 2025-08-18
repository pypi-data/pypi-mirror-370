"""
Test script to demonstrate the validation system
"""

import os
import sys
import json

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

try:
    from MediLink_Deductible_Validator import run_validation_comparison
except ImportError:
    print("Could not import MediLink_Deductible_Validator")
    sys.exit(1)

def create_sample_responses():
    """Create sample legacy and Super Connector responses for testing"""
    
    # Sample legacy API response
    legacy_response = {
        "memberPolicies": [
            {
                "policyInfo": {
                    "coverageType": "Medical",
                    "policyStatus": "Active"
                },
                "patientInfo": [
                    {
                        "lastName": "Smith",
                        "firstName": "John",
                        "middleName": "A"
                    }
                ],
                "insuranceInfo": {
                    "insuranceType": "PPO",
                    "insuranceTypeCode": "PPO",
                    "memberId": "123456789",
                    "payerId": "87726"
                },
                "deductibleInfo": {
                    "individual": {
                        "inNetwork": {
                            "remainingAmount": "500.00"
                        }
                    }
                }
            }
        ]
    }
    
    # Sample Super Connector API response (with some values in different locations)
    super_connector_response = {
        "lastName": "Smith",
        "firstName": "John", 
        "middleName": "A",
        "policyStatus": "Active",
        "planTypeDescription": "PPO",
        "productServiceCode": "PPO",
        "subscriberId": "123456789",
        "payerId": "87726",
        "metYearToDateAmount": "500.00",
        "rawGraphQLResponse": {
            "data": {
                "checkEligibility": {
                    "eligibility": [
                        {
                            "serviceLevels": [
                                {
                                    "individual": [
                                        {
                                            "services": [
                                                {
                                                    "service": "deductible",
                                                    "remainingAmount": "500.00"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    return legacy_response, super_connector_response

def main():
    """Test the validation system"""
    print("Testing MediLink Deductible Validation System")
    print("=" * 50)
    
    # Create sample responses
    legacy_response, super_connector_response = create_sample_responses()
    
    # Create output file path
    output_file_path = os.path.join(os.getenv('TEMP', '.'), 'test_validation_report.txt')
    
    # Run validation
    print("Running validation comparison...")
    validation_report = run_validation_comparison(
        legacy_response, 
        super_connector_response, 
        output_file_path
    )
    
    print("Validation completed!")
    print("Report saved to: {}".format(output_file_path))
    
    # Print summary
    print("\nSummary:")
    print("Total legacy values: {}".format(len(validation_report['legacy_values'])))
    print("Found in Super Connector: {}".format(len(validation_report['found_values'])))
    print("Missing from Super Connector: {}".format(len(validation_report['missing_values'])))
    
    # Open the report
    try:
        os.system('notepad.exe "{}"'.format(output_file_path))
    except:
        print("Could not open report in Notepad")

if __name__ == "__main__":
    main() 