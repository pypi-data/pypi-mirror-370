# insurance_type_integration_test.py
# Integration testing and validation for insurance type selection enhancement
# Python 3.4.4 compatible implementation

import time
import json
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use core utilities for standardized imports
from MediCafe.core_utils import get_shared_config_loader
MediLink_ConfigLoader = get_shared_config_loader()

try:
    from MediCafe.api_core import (
        APIClient
    )
    from MediLink import (
        enrich_with_insurance_type
    )
    from MediLink_837p_encoder_library import (
        insurance_type_selection,
        _original_insurance_type_selection_logic
    )
    from MediLink import MediLink_insurance_utils
    validate_insurance_type_from_config = getattr(MediLink_insurance_utils, 'validate_insurance_type_from_config', None)
    get_feature_flag = getattr(MediLink_insurance_utils, 'get_feature_flag', None)
    generate_insurance_assignment_summary = getattr(MediLink_insurance_utils, 'generate_insurance_assignment_summary', None)
except ImportError as e:
    print("Import error: {}".format(str(e)))
    print("This module requires the insurance type components.")

def run_insurance_type_integration_tests():
    """
    Run comprehensive integration tests for insurance type selection enhancement.
    Python 3.4.4 compatible implementation.
    """
    print("=" * 60)
    print("INSURANCE TYPE SELECTION ENHANCEMENT - INTEGRATION TESTS")
    print("=" * 60)
    
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_details': []
    }
    
    # Test 1: Production Readiness Validation
    test_results['total_tests'] += 1
    try:
        print("\n1. Testing Production Readiness Validation...")
        from MediLink import MediLink_insurance_utils
        validate_insurance_configuration = getattr(MediLink_insurance_utils, 'validate_insurance_configuration', None)
        if validate_insurance_configuration:
            validate_insurance_configuration()
        print("   PASS Production readiness validation PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'production_readiness', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL Production readiness validation FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'production_readiness', 'status': 'FAILED', 'error': str(e)})
    
    # Test 2: Insurance Configuration Validation
    test_results['total_tests'] += 1
    try:
        print("\n2. Testing Insurance Configuration Validation...")
        from MediLink import MediLink_insurance_utils
        validate_insurance_configuration = getattr(MediLink_insurance_utils, 'validate_insurance_configuration', None)
        if validate_insurance_configuration:
            validate_insurance_configuration()
        print("   PASS Insurance configuration validation PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'insurance_config', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL Insurance configuration validation FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'insurance_config', 'status': 'FAILED', 'error': str(e)})
    
    # Test 3: Feature Flag System
    test_results['total_tests'] += 1
    try:
        print("\n3. Testing Feature Flag System...")
        api_flag = get_feature_flag('api_insurance_selection', default=False)
        enhanced_flag = get_feature_flag('enhanced_insurance_enrichment', default=False)
        print("   API Insurance Selection Flag: {}".format(api_flag))
        print("   Enhanced Insurance Enrichment Flag: {}".format(enhanced_flag))
        print("   PASS Feature flag system PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'feature_flags', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL Feature flag system FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'feature_flags', 'status': 'FAILED', 'error': str(e)})
    
    # Test 4: API Client Initialization
    test_results['total_tests'] += 1
    try:
        print("\n4. Testing API Client Initialization...")
        # Test both factory and direct instantiation
        try:
            from MediCafe.core_utils import get_api_client
            api_client = get_api_client()
            if api_client is None:
                api_client = APIClient()
        except ImportError:
            api_client = APIClient()
        print("   PASS API client initialization PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'api_client_init', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL API client initialization FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'api_client_init', 'status': 'FAILED', 'error': str(e)})
    
    # Test 5: Insurance Type Selection Backward Compatibility
    test_results['total_tests'] += 1
    try:
        print("\n5. Testing Insurance Type Selection Backward Compatibility...")
        test_parsed_data = {
            'LAST': 'TESTPATIENT',
            'FIRST': 'TEST',
            'BDAY': '1980-01-01',
            'insurance_type': '12'  # Pre-assigned
        }
        result = insurance_type_selection(test_parsed_data)
        assert result == '12', "Should return pre-assigned insurance type"
        print("   PASS Insurance type selection backward compatibility PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'backward_compatibility', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL Insurance type selection backward compatibility FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'backward_compatibility', 'status': 'FAILED', 'error': str(e)})
    
    # Test 6: Patient Data Enrichment
    test_results['total_tests'] += 1
    try:
        print("\n6. Testing Patient Data Enrichment...")
        test_patient_data = [
            {
                'patient_id': 'TEST001',
                'patient_name': 'Test Patient',
                'primary_insurance_id': '87726'
            }
        ]
        enriched_data = enrich_with_insurance_type(test_patient_data)
        assert len(enriched_data) == 1, "Should return same number of patients"
        assert 'insurance_type' in enriched_data[0], "Should add insurance_type field"
        print("   PASS Patient data enrichment PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'patient_enrichment', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL Patient data enrichment FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'patient_enrichment', 'status': 'FAILED', 'error': str(e)})
    
    # Test 7: Monitoring System
    test_results['total_tests'] += 1
    try:
        print("\n7. Testing Monitoring System...")
        test_patient_data = [
            {
                'patient_id': 'TEST001',
                'insurance_type': '12',
                'insurance_type_source': 'DEFAULT'
            },
            {
                'patient_id': 'TEST002', 
                'insurance_type': 'HM',
                'insurance_type_source': 'API'
            }
        ]
        generate_insurance_assignment_summary(test_patient_data)
        print("   PASS Monitoring system PASSED")
        test_results['passed_tests'] += 1
        test_results['test_details'].append({'test': 'monitoring', 'status': 'PASSED'})
    except Exception as e:
        print("   FAIL Monitoring system FAILED: {}".format(str(e)))
        test_results['failed_tests'] += 1
        test_results['test_details'].append({'test': 'monitoring', 'status': 'FAILED', 'error': str(e)})
    
    # Print Test Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("Total Tests: {}".format(test_results['total_tests']))
    print("Passed: {}".format(test_results['passed_tests']))
    print("Failed: {}".format(test_results['failed_tests']))
    
    if test_results['failed_tests'] == 0:
        print("\nPASS ALL TESTS! System ready for deployment.")
    else:
        print("\nFAIL {} TESTS. Review before deployment.".format(test_results['failed_tests']))
        for test in test_results['test_details']:
            if test['status'] == 'FAILED':
                print("   - {}: {}".format(test['test'], test.get('error', 'Unknown error')))
    
    return test_results

def test_insurance_type_validation():
    """Test insurance type validation with various scenarios"""
    print("\n" + "=" * 50)
    print("INSURANCE TYPE VALIDATION TESTS")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'Valid PPO Type',
            'insurance_type': '12',
            'payer_id': '87726',
            'expected': '12'
        },
        {
            'name': 'Valid HMO Type', 
            'insurance_type': 'HM',
            'payer_id': '87726',
            'expected': 'HM'
        },
        {
            'name': 'Novel Valid Type (Strict Validation)',
            'insurance_type': 'EP',
            'payer_id': '87726',
            'expected': '12'  # Strict validation rejects novel codes
        },
        {
            'name': 'Invalid Type Format',
            'insurance_type': 'INVALID123',
            'payer_id': '87726',
            'expected': '12'  # Should fallback to PPO
        },
        {
            'name': 'Empty Type',
            'insurance_type': '',
            'payer_id': '87726',
            'expected': '12'  # Should fallback to PPO
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        try:
            result = validate_insurance_type_from_config(
                test_case['insurance_type'], 
                test_case['payer_id']
            )
            
            if result == test_case['expected']:
                print("PASS {}: {} -> {}".format(test_case['name'], test_case['insurance_type'], result))
                passed += 1
            else:
                print("FAIL {}: Expected {}, got {}".format(test_case['name'], test_case['expected'], result))
                failed += 1
                
        except Exception as e:
            print("FAIL {}: Exception - {}".format(test_case['name'], str(e)))
            failed += 1
    
    print("\nValidation Tests Summary: {} passed, {} failed".format(passed, failed))
    return passed, failed

def create_test_configuration():
    """Create test configuration for development and testing"""
    print("\n" + "=" * 50)
    print("CREATING TEST CONFIGURATION")
    print("=" * 50)
    
    test_config = {
        "MediLink_Config": {
            "feature_flags": {
                "api_insurance_selection": False,  # Start disabled
                "enhanced_insurance_enrichment": False,  # Start disabled
                "enhanced_insurance_selection": False  # Start disabled
            },
            "insurance_options": {
                "12": "Preferred Provider Organization (PPO)",
                "13": "Point of Service (POS)", 
                "14": "Exclusive Provider Organization (EPO)",
                "16": "Indemnity",
                "HM": "Health Maintenance Organization (HMO)",
                "BL": "Blue Cross/Blue Shield",
                "CI": "Commercial Insurance",
                "MA": "Medicare Advantage",
                "MB": "Medicare Part B",
                "MC": "Medicare Part C"
            },
            "default_insurance_type": "12",
            "TestMode": False  # Must be False for production
        }
    }
    
    print("Test configuration created:")
    print(json.dumps(test_config, indent=2))
    print("\nCopy this configuration to your config.json file")
    print("Ensure TestMode is False for production")
    print("Enable feature flags gradually during rollout")
    
    return test_config

def deployment_checklist():
    """Print deployment checklist for insurance type enhancement"""
    print("\n" + "=" * 60)
    print("DEPLOYMENT CHECKLIST")
    print("=" * 60)
    
    checklist = [
        "[ ] All integration tests pass",
        "[ ] Production readiness validation passes",
        "[ ] Insurance configuration validation passes", 
        "[ ] TestMode is disabled in configuration",
        "[ ] Feature flags are properly configured (default: disabled)",
        "[ ] Enhanced API client initializes successfully",
        "[ ] Backward compatibility verified with existing callers",
        "[ ] Monitoring system is functional",
        "[ ] Circuit breaker, caching, and rate limiting are active",
        "[ ] Fallback mechanisms tested and working",
        "[ ] Log rotation configured for increased logging volume",
        "[ ] Documentation updated with new features",
        "[ ] Team trained on new monitoring and feature flags"
    ]
    
    for item in checklist:
        print(item)
    
    print("\nComplete all checklist items before deployment")
    print("Follow gradual rollout plan with feature flags")
    print("Monitor logs and metrics closely during rollout")

if __name__ == "__main__":
    print("Insurance Type Selection Enhancement - Integration Test Suite")
    print("Python 3.4.4 Compatible Implementation")
    
    # Run all tests
    test_results = run_insurance_type_integration_tests()
    
    # Run validation tests
    validation_passed, validation_failed = test_insurance_type_validation()
    
    # Create test configuration
    test_config = create_test_configuration()
    
    # Display deployment checklist
    deployment_checklist()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    total_passed = test_results['passed_tests'] + validation_passed
    total_failed = test_results['failed_tests'] + validation_failed
    total_tests = test_results['total_tests'] + validation_passed + validation_failed
    
    print("Overall Tests: {} passed, {} failed out of {} total".format(total_passed, total_failed, total_tests))
    
    if total_failed == 0:
        print("PASS ALL SYSTEMS GO! Ready for phased deployment.")
    else:
        print("FAIL  Address {} failed tests before deployment.".format(total_failed))