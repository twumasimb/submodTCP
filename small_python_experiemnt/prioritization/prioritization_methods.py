import os
import ast
import time
import json
import astor 
import torch
import random
import numpy as np
from tqdm.auto import tqdm
from transformers import AutoTokenizer, AutoModel
from prioritization.utils import extract_source_functions, generate_embedding


def random_prioritization(tests, logger=None):
    """
    Randomly shuffle the test order.
    """
    if logger:
        logger.info("Starting random prioritization")
        
    shuffled = tests.copy()
    random.shuffle(shuffled)
    
    if logger:
        logger.info(f"Random prioritization complete. Shuffled {len(shuffled)} tests")

    print(shuffled[0])
        
    return shuffled


def semantic_prioritization(tests, logger=None):
    """
    Prioritize tests based on their semantic features.
    This implementation prioritizes:
    1. Tests with exception handling
    2. Tests with more assertions
    3. Tests of more complex functions (divide, power, square_root)
    """
    if logger:
        logger.info("Starting semantic prioritization")
        
    def score_test(test):
        features = test['semantic_features']
        score = 0
        
        # Tests with exception handling are important
        if features.get('tests_exceptions', False):
            score += 100
        
        # More assertions might mean more test coverage
        score += features.get('assertion_count', 0) * 10
        
        # Prioritize testing complex functions
        function_complexity = {
            'square_root': 50, 
            'divide': 40,
            'power': 30,
            'multiply': 20, 
            'subtract': 10,
            'add': 5
        }
        
        if 'tests_function' in features:
            score += function_complexity.get(features['tests_function'], 0)
        
        # Give weight to tests that call more unique functions
        score += len(features.get('unique_function_calls', [])) * 5
        
        return score
    
    # Sort tests by score in descending order
    prioritized = sorted(tests, key=score_test, reverse=True)
    
    if logger:
        logger.info(f"Semantic prioritization complete. Ordered {len(prioritized)} tests")
        # Log the top 5 tests and their features
        for i, test in enumerate(prioritized[:5]):
            logger.info(f"Top test #{i+1}: {test['full_name']}")
            logger.info(f"  Features: {test['semantic_features']}")
            
    return prioritized


def previous_failure_prioritization(tests, failure_history_file, logger=None):
    """
    Prioritize tests based on previous failure history.
    """
    if logger:
        logger.info(f"Starting previous failure prioritization using history file: {failure_history_file}")
        
    # Default scores if no history exists
    test_scores = {test['full_name']: 0 for test in tests}
    
    # Try to load failure history
    try:
        with open(failure_history_file, 'r') as f:
            failure_history = json.load(f)
            
        if logger:
            logger.info(f"Loaded failure history with {len(failure_history)} entries")
            
        # Higher score for failed tests
        for test_name, result in failure_history.items():
            if result == "FAIL":
                # Extract just the method name from the full test path
                # e.g. "test_divide" from "tests/test_v1.py::TestCalculator::test_divide"
                method_name = test_name.split("::")[-1]
                
                # Find all tests with this method name and increase their score
                for test in tests:
                    if test['method_name'] == method_name:
                        test_scores[test['full_name']] = 100
                        
                        if logger:
                            logger.info(f"Prioritizing test {test['full_name']} due to previous failure of {method_name}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # If no history file or invalid JSON, use default scores
        if logger:
            logger.warning(f"Could not load failure history: {str(e)}. Using default scores.")
        pass
    
    # Sort based on scores
    prioritized = sorted(tests, key=lambda test: test_scores.get(test['full_name'], 0), reverse=True)
    
    if logger:
        logger.info(f"Previous failure prioritization complete. Ordered {len(prioritized)} tests")
        # Log tests prioritized due to failure history
        prioritized_tests = [t for t in prioritized if test_scores.get(t['full_name'], 0) > 0]
        logger.info(f"Number of tests prioritized due to previous failures: {len(prioritized_tests)}")
        
    return prioritized


def submod_ordering(tests, source_dir="../v1", logger=None):
    """
    Prioritize tests using a submodular optimization approach with code embeddings.
    Uses UnixCoder to embed functions and test cases, then greedily selects tests
    that maximize marginal similarity gain.
    """
    
    if logger:
        logger.info("Loading UnixCoder model for code embeddings...")
    
    # Load UnixCoder model and tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained("microsoft/unixcoder-base")
        model = AutoModel.from_pretrained("microsoft/unixcoder-base")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model.to(device)
        if logger:
            logger.info(f"Successfully loaded UnixCoder model and tokenizer to {device}")
    except Exception as e:
        if logger:
            logger.error(f"Error loading UnixCoder: {str(e)}")
    
    # Extract source code functions
    source_functions = extract_source_functions(source_dir, logger)
    
    # Generate embeddings for source functions
    function_embeddings = []
    for func in tqdm(source_functions, desc="Embedding functions"):
        embedding = generate_embedding(func['code'], tokenizer, model)
        function_embeddings.append(embedding)
    
    function_embeddings = np.array(function_embeddings)
        
    if logger:
        logger.info(f"Generated embeddings for {len(function_embeddings)} source functions")
    
    # Generate embeddings for test cases
    test_embeddings = []
    for test in tqdm(tests, desc="Embedding tests"):
        embedding = generate_embedding(test['code'], tokenizer, model)
        test_embeddings.append(embedding)
    
    test_embeddings = np.array(test_embeddings)
    
    if logger:
        logger.info(f"Generated embeddings for {len(test_embeddings)} test cases")
    
    # Submodular function optimization with greedy algorithm
    if logger:
        logger.info("Running submodular optimization...")
    
    def similarity(embedding_a, embedding_b):
        """Calculate cosine similarity between two embeddings"""
        return np.dot(embedding_a, embedding_b) / (np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b))
    
    def calculate_gain(selected_indices, candidate_index):
        """
        Calculate the marginal gain of adding a new test
        This implements a facility location objective function, which is submodular
        """
        if not selected_indices:
            # For the first selection, just use max similarity to any function
            similarities = [similarity(test_embeddings[candidate_index], func_embedding) 
                           for func_embedding in function_embeddings]
            return np.mean(similarities)
        
        # For subsequent selections, calculate marginal gain
        gain = 0
        for func_idx, func_embedding in enumerate(function_embeddings):
            # Current max similarity for this function from selected tests
            current_max = max([similarity(test_embeddings[idx], func_embedding) for idx in selected_indices])
            # Max similarity if we add the candidate test
            new_sim = similarity(test_embeddings[candidate_index], func_embedding)
            # Add the marginal gain (limited to positive values)
            gain += max(0, new_sim - current_max)
        
        return gain
    
    # Greedy selection
    remaining_indices = set(range(len(tests)))
    selected_indices = []
    prioritized_tests = []
    
    start_time = time.time()
    while remaining_indices:
        best_gain = -float('inf')
        best_idx = None
        
        for idx in remaining_indices:
            gain = calculate_gain(selected_indices, idx)
            if gain > best_gain:
                best_gain = gain
                best_idx = idx
        
        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)
        prioritized_tests.append(tests[best_idx])
        
        if logger and len(selected_indices) % 10 == 0:
            logger.info(f"Selected {len(selected_indices)}/{len(tests)} tests")
    
    end_time = time.time()
    if logger:
        logger.info(f"Submodular optimization complete in {end_time - start_time:.2f} seconds")
        logger.info(f"First 5 selected tests:")
        for i, test in enumerate(prioritized_tests[:5]):
            logger.info(f"  {i+1}. {test['full_name']}")
    
    return prioritized_tests
