import os
import sys
import argparse
import random
from typing import List, Dict, Any

# Add parent directory to path so we can import the utils module
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from prioritization.utils import get_all_tests, evaluate_fault_detection_efficiency
from prioritization.logging_utils import setup_logging
from prioritization.prioritization_methods import (
    random_prioritization,
    semantic_prioritization,
    previous_failure_prioritization,
    submod_ordering,
)

def create_test_bash_script(prioritized_tests: List[Dict[str, Any]], output_file: str, logger, version:str = "v1"):
    """Create a bash script to run tests in prioritized order using pytest."""
    logger.info(f"Creating bash script: {output_file}")
    
    with open(output_file, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("# This script was auto-generated to run tests in prioritized order\n\n")
        
        for test in prioritized_tests:
            test_name = test.get('method_name', '')
            test_file = test.get('file_path', '')
            class_name = test.get('class_name', '')
            
            # Format the pytest command exactly as requested
            command = f'pytest tests/test_calculator.py::{class_name}::{test_name} -v -k "{version}"'
            
            f.write(f"{command}\n")
    
    # Make the script executable
    os.chmod(output_file, 0o755)
    logger.info(f"Bash script {output_file} created successfully and made executable.")

def main():
    """Main function to generate a bash script for running prioritized tests."""
    parser = argparse.ArgumentParser(description="Generate bash script for test prioritization")
    parser.add_argument("--test-dir", default="../tests", 
                        help="Directory containing test files")
    parser.add_argument("--method", choices=["random", "semantic", "failure", "submod"], 
                        default="random", help="Prioritization method to use")
    parser.add_argument("--failure-history", default="../test_results.json",
                       help="JSON file containing test failure history")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--source-dir", default="../v1",
                       help="Directory containing source code (for submod method)")
    parser.add_argument("--bash-output", default="run_prioritized_tests.sh",
                        help="Output file for the bash script (default: run_prioritized_tests.sh)")
    parser.add_argument("--log-level", default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    parser.add_argument("--source_dir", default="v1", help="Location of the software file")
    
    # Add back arguments needed for setup_logging compatibility
    parser.add_argument("--run", action="store_true",
                        help="Placeholder to maintain compatibility with setup_logging")
    parser.add_argument("--evaluate", action="store_true",
                        help="Placeholder to maintain compatibility with setup_logging")
    
    args = parser.parse_args()

    # Set up logging
    logger = setup_logging(args.method, args)

    # Log script start
    logger.info("===== Bash Script Generator Started =====")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        logger.info(f"Random seed set to {args.seed}")
    
    # Get absolute path for test directory
    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), args.test_dir))
    logger.info(f"Test directory: {test_dir}")
    
    # Get all tests with semantic features
    logger.info("Retrieving and analyzing test files...")
    tests = get_all_tests(test_dir)
    
    if not tests:
        logger.error(f"No tests found in {test_dir}")
        return
    
    logger.info(f"Found {len(tests)} tests")
    
    # Apply selected prioritization method
    if args.method == "random":
        prioritized_tests = random_prioritization(tests, logger)
    elif args.method == "semantic":
        prioritized_tests = semantic_prioritization(tests, logger)
    elif args.method == "failure":
        prioritized_tests = previous_failure_prioritization(tests, args.failure_history, logger)
    elif args.method == "submod":
        prioritized_tests = submod_ordering(tests, args.source_dir, logger)

    # Evaluate APFD and other metrics
    logger.info("Calculating APFD and other fault detection metrics...")
    efficiency_metrics = evaluate_fault_detection_efficiency(prioritized_tests)
    apfd_score = efficiency_metrics.get('apfd', 0)
    logger.info(f"APFD Score: {apfd_score:.4f}")

    # Generate bash script
    create_test_bash_script(prioritized_tests, args.bash_output, logger)
    logger.info(f"To run tests in prioritized order, execute: bash {args.bash_output}")
    
    logger.info("===== Bash Script Generator Completed =====")

if __name__ == "__main__":
    main()