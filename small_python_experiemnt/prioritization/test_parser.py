import ast
import os
import inspect
import importlib.util
from typing import Dict, List, Any, Optional, Set

def parse_test_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a test file to extract fixtures, test classes, and test functions.
    
    Args:
        file_path: Path to the test file
    
    Returns:
        Dictionary containing information about the test file
    """
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Parse the file with AST
    tree = ast.parse(file_content)
    
    # Extract information
    result = {
        'file_path': file_path,
        'fixtures': [],
        'classes': [],
        'functions': []
    }
    
    for node in ast.walk(tree):
        # Find fixtures (functions with @pytest.fixture decorator)
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Call) and 
                    isinstance(decorator.func, ast.Attribute) and 
                    decorator.func.attr == 'fixture'):
                    
                    result['fixtures'].append({
                        'name': node.name,
                        'lineno': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'has_params': any(kwd.arg == 'params' for kwd in decorator.keywords)
                    })
        
        # Find test classes
        elif isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            class_info = {
                'name': node.name,
                'methods': []
            }
            
            for method in [n for n in node.body if isinstance(n, ast.FunctionDef)]:
                if method.name.startswith('test_'):
                    class_info['methods'].append({
                        'name': method.name,
                        'args': [arg.arg for arg in method.args.args if arg.arg != 'self'],
                    })
            
            result['classes'].append(class_info)
        
        # Find standalone test functions
        elif isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            result['functions'].append({
                'name': node.name,
                'args': [arg.arg for arg in node.args.args]
            })
    
    return result

def get_fixture_dependencies(test_info: Dict[str, Any]) -> Set[str]:
    """Extract fixtures required by a test function."""
    fixtures = set()
    
    # For class methods
    if test_info.get('class_name'):
        for cls_info in test_info.get('file_fixtures', {}).get('classes', []):
            if cls_info['name'] == test_info['class_name']:
                for method in cls_info['methods']:
                    if method['name'] == test_info['method_name']:
                        fixtures.update(method['args'])
    
    # For standalone functions
    else:
        for func in test_info.get('file_fixtures', {}).get('functions', []):
            if func['name'] == test_info['method_name']:
                fixtures.update(func['args'])
    
    return fixtures

def load_module_from_file(file_path: str) -> Any:
    """Load a Python module from file path."""
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
