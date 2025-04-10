# APFD Summary Report - submod

## Effectiveness Metrics

- **APFD Score**: 0.8750
- **Total Tests**: 12
- **Total Faults**: 2
- **Average Position of Fault Detection**: 2.00
- **Percentage of Tests Needed to Find All Faults**: 25.00%

## Fault Detection Positions

| Fault | Detected at Position | Detected by Test |
|------|---------------------|------------------|
| unknown_fault | 1 | test_divide |
| combined_operations | 3 | test_combined_operations |

## Test Execution Order

| # | Test Name | Status |
|---|-----------|--------|
| 1 | test_divide | ❌ FAILED |
| 2 | test_square_root | ❌ FAILED |
| 3 | test_combined_operations | ❌ FAILED |
| 4 | test_average | ✅ PASSED |
| 5 | test_gcd | ❌ FAILED |
| 6 | test_factorial | ❌ FAILED |
| 7 | test_subtract | ✅ PASSED |
| 8 | test_add | ✅ PASSED |
| 9 | test_absolute | ✅ PASSED |
| 10 | test_modulus | ❌ FAILED |
| 11 | test_multiply | ✅ PASSED |
| 12 | test_power | ❌ FAILED |