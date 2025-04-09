import json
import matplotlib.pyplot as plt
from prioritization.utils import evaluate_fault_detection_efficiency

def save_prioritized_order(tests, output_file, logger=None):
    """
    Save the prioritized test order to a file.
    
    Args:
        tests: Prioritized list of tests
        output_file: Path to output file
        logger: Logger instance for tracking execution
    """
    if logger:
        logger.info(f"Saving prioritized test order to {output_file}")
        
    with open(output_file, 'w') as f:
        ordered_tests = [test['full_name'] for test in tests]
        json.dump(ordered_tests, f, indent=2)
    
    if logger:
        logger.info(f"Prioritized test order saved successfully")
    else:
        print(f"Prioritized test order saved to {output_file}")


def print_prioritized_order(tests, logger=None):
    """
    Print the prioritized test order to the console.
    
    Args:
        tests: Prioritized list of tests
        logger: Logger instance for tracking execution
    """
    header = "Prioritized Test Order:"
    divider = "-" * 60
    
    print(header)
    print(divider)
    
    if logger:
        logger.info(header)
        logger.info(divider)
    
    for i, test in enumerate(tests, 1):
        line = f"{i}. {test['full_name']}"
        print(line)
        
        if logger:
            logger.info(line)
    
    print(divider)
    
    if logger:
        logger.info(divider)


def evaluate_prioritization_method(tests, method_name, logger=None):
    """
    Evaluate how well a prioritization method detects faults.
    
    Args:
        tests: Prioritized list of test dictionaries
        method_name: Name of the prioritization method used
        logger: Logger instance for tracking execution
    """
    if logger:
        logger.info(f"Evaluating fault detection efficiency for {method_name}")
        
    results = evaluate_fault_detection_efficiency(tests)
    
    header = f"\nFault Detection Results for {method_name}:"
    divider = "-" * 60
    
    print(header)
    print(divider)
    
    if logger:
        logger.info(header)
        logger.info(divider)
    
    metrics = [
        f"Total tests: {results['total_tests']}",
        f"Total faults: {results['total_faults']}",
        f"APFD score: {results['apfd']:.4f}",
        f"Average fault detection position: {results['avg_fault_detection_position']:.2f}",
        f"Percentage of tests needed to find all faults: {results['tests_needed_percentage']:.2f}%"
    ]
    
    for metric in metrics:
        print(metric)
        if logger:
            logger.info(metric)
    
    print("\nFaults found at positions:")
    if logger:
        logger.info("Faults found at positions:")
        
    for fault, position in results['fault_detection_positions'].items():
        position_info = f"  {fault}: Test #{position}"
        print(position_info)
        if logger:
            logger.info(position_info)
    
    print(divider)
    if logger:
        logger.info(divider)
    
    return results


def plot_error_detection(test_results, method_name, output_path=None, logger=None):
    """
    Generate a plot showing the number of tests run vs. number of errors detected.
    
    Args:
        test_results: Dictionary containing test results
        method_name: Name of the prioritization method
        output_path: Path to save the plot (if None, plot is displayed but not saved)
        logger: Logger instance for tracking execution
    """
    if logger:
        logger.info(f"Generating error detection plot for {method_name}")
        
    plt.figure(figsize=(10, 6))
    
    # Extract data points
    tests_run = [point[0] for point in test_results['error_detection']]
    errors_found = [point[1] for point in test_results['error_detection']]
    
    # Create the plot
    plt.plot(tests_run, errors_found, marker='o', linestyle='-')
    plt.xlabel('Number of Tests Run')
    plt.ylabel('Number of Errors Detected')
    plt.title(f'Error Detection Rate - {method_name}')
    plt.grid(True)
    
    # Improve appearance
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        if logger:
            logger.info(f"Error detection plot saved to {output_path}")
        else:
            print(f"Error detection plot saved to {output_path}")
    else:
        plt.show()
        if logger:
            logger.info("Error detection plot displayed (not saved)")