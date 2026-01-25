"""
Test runner for Phase 4B Module 2 tests
"""
import sys
import subprocess

print("="*60)
print("Running Module 2 Tests")
print("="*60)

# Test 1: Materials module
print("\n1. Testing materials module...")
result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "rocket_sim/system_model/tests/test_materials.py",
     "-v", "--tb=short"],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Test 2: Burst calculator module
print("\n2. Testing burst_calculator module...")
result = subprocess.run(
    [sys.executable, "-m", "pytest",
     "rocket_sim/system_model/tests/test_burst_calculator.py",
     "-v", "--tb=short"],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print(result.stderr)

print("\n" + "="*60)
print("Test run complete")
print("="*60)
