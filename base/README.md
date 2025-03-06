# Submodular Test Case Prioritization Experiment

This project implements and evaluates submodular optimization approaches for test case prioritization.

## Project Structure

- `library_system.py`: Sample library management system implementation
- `test_library.py`: Test cases for the library system
- `test_prioritization.py`: Implementation of submodular functions and prioritization logic
- `experiment_runner.py`: Code to run experiments and generate visualizations

## Submodular Functions

1. Coverage-based Function
   - Maximizes the number of unique code elements covered
   - Provides the (1-1/e) approximation guarantee

2. Diversity-based Function
   - Maximizes the diversity between selected test cases
   - Uses Jaccard distance as the diversity measure

3. Combined Function
   - Weighted combination of coverage and diversity
   - Allows tuning via the alpha parameter

## Evaluation Metrics

1. APFD (Average Percentage of Faults Detected)
   - Measures how quickly faults are detected in the prioritized order

2. FDR (Fault Detection Rate)
   - Shows the percentage of faults detected as tests are executed
   - Plotted as a curve to show detection rate over time

## Running Experiments

1. Install dependencies:
```bash
pip install numpy matplotlib
```

2. Run the experiments:
```bash
python experiment_runner.py
```

This will:
- Extract test cases from the library system
- Run prioritization with different submodular functions
- Generate plots comparing the approaches
- Print APFD scores for each method

## Extending the Experiments

To experiment with different parameters:

1. Modify the alpha value in CombinedFunction to adjust the coverage-diversity trade-off
2. Add new submodular functions by extending the SubmodularFunction class
3. Add more test cases to test_library.py
4. Modify the fault matrix in ExperimentRunner to simulate different fault scenarios