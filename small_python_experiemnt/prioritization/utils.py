import os
import re
import ast
import astor 
import torch
import inspect
import subprocess
import importlib.util
from typing import List, Dict, Any, Callable, Optional, Tuple


def extract_source_functions(source_dir, logger=None):
    """
    Extract function definitions from Python files in the given source directory.
    
    Args:
        source_dir (str): Directory containing Python source files to analyze
        logger: Optional logger object for logging information
        
    Returns:
        list: List of dictionaries containing function names and code
    """
    source_functions = []
    for file in os.listdir(os.path.abspath(source_dir)):
        if file.endswith(".py"):
            file_path = os.path.join(os.path.abspath(source_dir), file)
            if logger:
                logger.info(f"Analyzing source file: {file_path}")
                
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Use AST to extract functions
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        function_name = node.name
                        function_body = astor.to_source(node)
                        source_functions.append({
                            'name': function_name,
                            'code': function_body
                        })
            except SyntaxError as e:
                if logger:
                    logger.error(f"Syntax error in {file_path}: {str(e)}")
    
    if logger:
        logger.info(f"Found {len(source_functions)} functions in source code")
        for func in source_functions:
            logger.debug(f"Function: {func['name']}")
            
    return source_functions


def generate_embedding(text, tokenizer, model, max_length=512):
    """
    Generate an embedding for a piece of code text using the provided tokenizer and model.
    
    Args:
        text (str): The code text to embed
        tokenizer: The tokenizer to use for tokenizing the text
        model: The model to use for generating embeddings
        max_length (int, optional): Maximum token length. Defaults to 512.
        
    Returns:
        numpy.ndarray: The embedding vector for the provided code
    """
    tokens = tokenizer.tokenize(text)
    tokens = tokens[:max_length]  # Truncate to max length
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    input_ids = torch.tensor([tokenizer.cls_token_id] + token_ids + [tokenizer.eos_token_id]).unsqueeze(0)
    
    # Move input_ids to the same device as the model
    device = next(model.parameters()).device
    input_ids = input_ids.to(device)
    
    with torch.no_grad():
        output = model(input_ids)
        embedding = output.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
    
    return embedding

def load_module_from_file(file_path: str) -> Any:
    """
    Dynamically load a Python module from a file path.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Loaded module object
    """
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_test_methods(test_file_path: str) -> List[Tuple[str, Callable]]:
    """
    Extract all test methods from a test file.
    
    Args:
        test_file_path: Path to the test file
        
    Returns:
        List of tuples containing (method_name, method_object)
    """
    module = load_module_from_file(test_file_path)
    test_methods = []
    
    for name, obj in inspect.getmembers(module):
        # Look for classes that might contain test methods
        if inspect.isclass(obj) and name.startswith('Test'):
            # Get all methods from the class
            for method_name, method_obj in inspect.getmembers(obj, inspect.isfunction):
                if method_name.startswith('test_'):
                    test_methods.append((f"{name}::{method_name}", method_obj))
    
    return test_methods


def extract_test_methods_from_ast(test_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract test methods using AST for more detailed analysis.
    
    Args:
        test_file_path: Path to the test file
        
    Returns:
        List of dictionaries containing method info
    """
    with open(test_file_path, 'r') as file:
        code = file.read()
    
    tree = ast.parse(code)
    test_methods = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            class_name = node.name
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                    method_info = {
                        'class_name': class_name,
                        'method_name': item.name,
                        'full_name': f"{class_name}::{item.name}",
                        'lineno': item.lineno,
                        'code': ast.unparse(item),
                        'ast_node': item,
                        'assertions': len([n for n in ast.walk(item) if isinstance(n, ast.Assert)])
                    }
                    test_methods.append(method_info)
    
    return test_methods


def extract_semantic_features(method_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract semantic features from a test method.
    
    Args:
        method_info: Dictionary containing method information
        
    Returns:
        Dictionary with semantic features
    """
    features = {
        'assertion_count': method_info['assertions'],
        'code_length': len(method_info['code']),
    }
    
    # Check which functionality is being tested
    method_name = method_info['method_name']
    calculator_functions = ['add', 'subtract', 'multiply', 'divide', 'power', 'square_root']
    
    for func in calculator_functions:
        if func in method_name:
            features['tests_function'] = func
            break
    
    # Extract function calls
    code = method_info['code']
    function_calls = re.findall(r'calculator\.([a-zA-Z_]+)\(', code)
    features['function_calls'] = function_calls
    features['unique_function_calls'] = list(set(function_calls))
    
    # Check for exception testing
    features['tests_exceptions'] = 'pytest.raises' in code
    
    return features


def find_test_files(directory: str, pattern: str = "test_*.py") -> List[str]:
    """
    Find all test files in a directory matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern to match filenames
        
    Returns:
        List of test file paths
    """
    test_files = []
    import glob
    
    for file_path in glob.glob(os.path.join(directory, pattern)):
        if os.path.isfile(file_path):
            test_files.append(file_path)
    
    return test_files


def get_all_tests(test_dir: str) -> List[Dict[str, Any]]:
    """
    Get all tests from a directory with their semantic features.
    
    Args:
        test_dir: Directory containing test files
        
    Returns:
        List of dictionaries with test information and features
    """
    test_files = find_test_files(test_dir)
    all_tests = []
    
    for file_path in test_files:
        # Skip the version-specific wrappers
        if "test_v0.py" in file_path or "test_v1.py" in file_path:
            continue
            
        methods = extract_test_methods_from_ast(file_path)
        for method in methods:
            semantic_features = extract_semantic_features(method)
            method.update({'semantic_features': semantic_features})
            all_tests.append(method)
    
    return all_tests


def evaluate_fault_detection_efficiency(prioritized_tests: List[Dict[str, Any]], 
                                       test_command: str = "pytest {test_name} -v") -> Dict[str, Any]:
    """
    Evaluates how quickly the prioritized test order finds faults in the code.
    
    Args:
        prioritized_tests: List of test dictionaries in prioritized order
        test_command: Command template to execute tests, with {test_name} placeholder
        
    Returns:
        Dictionary with statistics about fault detection efficiency
    """
    total_tests = len(prioritized_tests)
    detected_faults = set()
    all_faults = set()  # We'll populate this as we find faults
    fault_detection_positions = {}
    tests_executed = 0
    
    print("Evaluating fault detection efficiency...")
    
    for i, test in enumerate(prioritized_tests, 1):
        test_name = test['full_name'].replace('::', '.')
        test_path = f"tests/test_v1.py::{test_name}"
        
        # Run the test and check if it fails (which means it detected a fault)
        cmd = test_command.format(test_name=test_path)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        tests_executed += 1
        is_failure = result.returncode != 0
        
        if is_failure:
            # Extract the error type from the output
            error_lines = [line for line in result.stderr.split('\n') 
                          if 'ERROR' in line or 'FAILED' in line]
            
            for error_line in error_lines:
                # Try to extract what kind of error was found
                if "ZeroDivisionError" in result.stdout:
                    fault_type = "division_by_zero"
                elif "AssertionError" in result.stdout:
                    if "power" in test_name:
                        fault_type = "negative_exponent"
                    elif "square_root" in test_name:
                        fault_type = "incorrect_sqrt"
                    else:
                        fault_type = f"assertion_in_{test['method_name']}"
                else:
                    fault_type = f"unknown_fault_{len(all_faults)}"
                
                all_faults.add(fault_type)
                
                if fault_type not in detected_faults:
                    detected_faults.add(fault_type)
                    fault_detection_positions[fault_type] = i
                    print(f"Fault '{fault_type}' detected by test #{i}: {test_name}")
    
    # Calculate efficiency metrics
    if all_faults:
        # APFD (Average Percentage of Fault Detection)
        # APFD = 1 - (sum(first_position_of_each_fault) / (num_tests * num_faults)) + (1 / (2 * num_tests))
        sum_positions = sum(fault_detection_positions.values())
        apfd = 1 - (sum_positions / (total_tests * len(all_faults))) + (1 / (2 * total_tests))
        
        # Average position where faults were found
        avg_position = sum_positions / len(all_faults) if all_faults else 0
        
        # Percentage of tests needed to find all faults
        tests_needed_percentage = max(fault_detection_positions.values()) / total_tests * 100 if fault_detection_positions else 0
    else:
        apfd = 0
        avg_position = 0
        tests_needed_percentage = 0
    
    return {
        'total_tests': total_tests,
        'total_faults': len(all_faults),
        'detected_faults': len(detected_faults),
        'apfd': apfd,
        'avg_fault_detection_position': avg_position,
        'tests_needed_percentage': tests_needed_percentage,
        'fault_detection_positions': fault_detection_positions,
        'all_faults': list(all_faults)
    }


def run_test_with_coverage(test_name: str, source_dir: str = "v1") -> Tuple[bool, Dict[str, Any]]:
    """
    Run a single test with coverage analysis to determine which code it exercises.
    
    Args:
        test_name: Full test name (e.g. 'TestCalculator::test_divide')
        source_dir: Directory containing source code to measure coverage for
        
    Returns:
        Tuple of (passed, coverage_data)
    """
    try:
        import coverage
    except ImportError:
        print("Coverage package not installed. Install with: pip install coverage")
        return False, {}
    
    # Setup coverage
    cov = coverage.Coverage(source=[source_dir])
    cov.start()
    
    # Run the test
    test_path = f"tests/test_v1.py::{test_name.replace('::', '.')}"
    cmd = f"pytest {test_path} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    passed = result.returncode == 0
    
    # Stop coverage and get results
    cov.stop()
    cov.save()
    
    # Analyze which lines were covered
    coverage_data = {}
    for filename in cov.get_data().measured_files():
        if source_dir in filename:
            line_nums = cov.get_data().lines(filename)
            coverage_data[filename] = line_nums
    
    return passed, coverage_data


def get_fault_detection_mapping() -> Dict[str, List[str]]:
    """
    Creates a mapping of which tests detect which faults in the v1 calculator.
    This is specifically mapped for the calculator example.
    
    Returns:
        Dictionary mapping fault names to the tests that detect them
    """
    return {
        "division_by_zero": ["TestCalculator::test_divide"],
        "negative_exponent": ["TestCalculator::test_power"],
        "incorrect_sqrt": ["TestCalculator::test_square_root"],
        "subtraction_logic": []  # This fault isn't detected by the current tests
    }
