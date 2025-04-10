# APFD Summary Report - random

## Effectiveness Metrics

- **APFD Score**: 0.5417
- **Total Tests**: 12
- **Total Faults**: 2
- **Average Position of Fault Detection**: 6.00
- **Percentage of Tests Needed to Find All Faults**: 83.33%

## Fault Detection Positions

| Fault | Detected at Position | Detected by Test |
|------|---------------------|------------------|
| unknown_fault | 2 | test_gcd |
| combined_operations | 10 | test_combined_operations |

## Test Execution Order

| # | Test Name | Status |
|---|-----------|--------|
| 1 | test_add | ✅ PASSED |
| 2 | test_gcd | ❌ FAILED |
| 3 | test_average | ✅ PASSED |
| 4 | test_power | ❌ FAILED |
| 5 | test_square_root | ❌ FAILED |
| 6 | test_modulus | ❌ FAILED |
| 7 | test_factorial | ❌ FAILED |
| 8 | test_multiply | ✅ PASSED |
| 9 | test_divide | ❌ FAILED |
| 10 | test_combined_operations | ❌ FAILED |
| 11 | test_absolute | ✅ PASSED |
| 12 | test_subtract | ✅ PASSED |