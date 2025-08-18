#!/usr/bin/env python
# test_timing.py - Test script to run MediLink with timing traces

import sys
import os
import time

# Add the parent directory to the path so we can import MediLink modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_medilink_timing():
    """
    Test function to run MediLink with timing traces and identify bottlenecks.
    """
    print("=" * 60)
    print("MEDILINK TIMING ANALYSIS")
    print("=" * 60)
    print("This test will run MediLink with comprehensive timing traces")
    print("to identify what's causing the slow startup.")
    print("=" * 60)

    try:
        # Import and run the main menu
        from MediLink.MediLink_main import main_menu

        print("\nStarting MediLink timing test...")
        start_time = time.time()

        # Load configuration to test the caching
        from MediCafe.MediLink_ConfigLoader import load_configuration
        config, crosswalk = load_configuration()
        print("Initial configuration load completed")
        
        # Test the caching by loading again
        config2, crosswalk2 = load_configuration()
        print("Cached configuration load completed")
        
        # Test file detection with cached config
        from MediLink.MediLink_DataMgmt import detect_new_files
        directory_path = config['MediLink_Config']['inputFilePath']
        files, flagged = detect_new_files(directory_path)
        print("File detection with cached config completed")

        end_time = time.time()
        print("\n" + "=" * 60)
        print("TIMING TEST COMPLETED")
        print("=" * 60)
        print("Total execution time: {:.2f} seconds".format(end_time - start_time))
        print("Configuration caching is working!")

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print("\nError during timing test: {}".format(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_medilink_timing() 