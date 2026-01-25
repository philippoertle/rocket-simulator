"""
Phase 5 Verification & Validation Test Runner

Executes comprehensive test suite and generates validation report.

Usage:
    python run_phase5_validation.py
"""

import sys
import subprocess
import time
import json
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_command(cmd, description):
    """Run command and capture output."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}\n")

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_time

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    print(f"\nCompleted in {elapsed:.2f} seconds")
    print(f"Return code: {result.returncode}\n")

    return result.returncode == 0, result.stdout, elapsed


def main():
    print_header("PHASE 5: VERIFICATION & VALIDATION")
    print("PET Rocket Simulator - Comprehensive Test Suite")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = {}

    # Test 1: Unit Tests (All Modules)
    print_header("1. UNIT TESTS - All Modules")
    success, output, elapsed = run_command(
        [sys.executable, "-m", "pytest", "rocket_sim/", "-v", "--tb=short"],
        "Running unit tests for all modules"
    )
    results['unit_tests'] = {
        'success': success,
        'elapsed': elapsed,
        'output_lines': len(output.split('\n'))
    }

    # Test 2: Integration & Validation Tests
    print_header("2. INTEGRATION & VALIDATION TESTS")
    success, output, elapsed = run_command(
        [sys.executable, "-m", "pytest", "tests/test_phase5_validation.py", "-v", "--tb=short"],
        "Running Phase 5 validation tests"
    )
    results['validation_tests'] = {
        'success': success,
        'elapsed': elapsed
    }

    # Test 3: Code Coverage
    print_header("3. CODE COVERAGE ANALYSIS")
    success, output, elapsed = run_command(
        [sys.executable, "-m", "pytest", "--cov=rocket_sim", "--cov-report=term",
         "--cov-report=html", "rocket_sim/", "-v"],
        "Generating code coverage report"
    )
    results['coverage'] = {
        'success': success,
        'elapsed': elapsed
    }

    # Extract coverage percentage if available
    for line in output.split('\n'):
        if 'TOTAL' in line and '%' in line:
            parts = line.split()
            for part in parts:
                if '%' in part:
                    try:
                        coverage_pct = float(part.replace('%', ''))
                        results['coverage']['percentage'] = coverage_pct
                    except:
                        pass

    # Test 4: Performance Benchmark
    print_header("4. PERFORMANCE BENCHMARK")
    print("Running single simulation performance test...")

    start_time = time.time()
    try:
        from rocket_sim.integration.full_simulation import FullSimulationConfig, run_complete_simulation

        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.01,  # Full 10ms simulation
            max_step=1e-5
        )

        result = run_complete_simulation(config, verbose=False)
        elapsed = time.time() - start_time

        print(f"✅ Single simulation completed in {elapsed:.3f} seconds")
        print(f"   Peak pressure: {result.summary['peak_pressure']/1e5:.2f} bar")
        print(f"   Safety margin: {result.safety_margin:.2f}")
        print(f"   Status: {'FAILED' if result.failed else 'SAFE'}")

        results['performance'] = {
            'success': elapsed < 5.0,
            'elapsed': elapsed,
            'target': 5.0,
            'meets_nfr5': elapsed < 300.0  # <5 min requirement
        }

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        results['performance'] = {
            'success': False,
            'error': str(e)
        }

    # Test 5: Quick Integration Example
    print_header("5. INTEGRATION EXAMPLE - Safe vs Dangerous")

    try:
        from rocket_sim.integration.full_simulation import FullSimulationConfig, run_complete_simulation

        # Safe configuration
        config_safe = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            cap_type="hemispherical",
            include_threads=False,
            combustion_time=0.001
        )

        result_safe = run_complete_simulation(config_safe, verbose=False)

        # Dangerous configuration
        config_danger = FullSimulationConfig(
            volume=0.001,
            fuel_oxidizer_ratio=2.5,
            cap_type="flat",
            vessel_thickness=0.0002,
            include_threads=True,
            combustion_time=0.001
        )

        result_danger = run_complete_simulation(config_danger, verbose=False)

        print("Safe Configuration (hemispherical cap):")
        print(f"  Safety margin: {result_safe.safety_margin:.2f}")
        print(f"  Status: {'FAILED' if result_safe.failed else 'SAFE'}")
        print(f"  Warnings: {len(result_safe.warnings)}")

        print("\nDangerous Configuration (flat cap, thin wall):")
        print(f"  Safety margin: {result_danger.safety_margin:.2f}")
        print(f"  Status: {'FAILED' if result_danger.failed else 'SAFE'}")
        print(f"  Warnings: {len(result_danger.warnings)}")
        print(f"  Failure location: {result_danger.failure_location}")

        results['integration_example'] = {
            'success': True,
            'safe_margin': result_safe.safety_margin,
            'danger_margin': result_danger.safety_margin,
            'conservative': result_danger.safety_margin < result_safe.safety_margin
        }

    except Exception as e:
        print(f"❌ Integration example failed: {e}")
        results['integration_example'] = {
            'success': False,
            'error': str(e)
        }

    # Summary
    print_header("VALIDATION SUMMARY")

    total_success = sum(1 for r in results.values() if r.get('success', False))
    total_tests = len(results)

    print(f"Tests Passed: {total_success}/{total_tests}")
    print(f"\nDetailed Results:")

    for test_name, test_result in results.items():
        status = "✅ PASS" if test_result.get('success') else "❌ FAIL"
        elapsed = test_result.get('elapsed', 0)
        print(f"  {test_name:25s} {status:10s} ({elapsed:.2f}s)")

        if 'percentage' in test_result:
            print(f"    Coverage: {test_result['percentage']:.1f}%")
        if 'meets_nfr5' in test_result:
            nfr_status = "✅" if test_result['meets_nfr5'] else "❌"
            print(f"    NFR-5 (<5 min): {nfr_status}")

    # Save results
    results_file = Path("validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n Results saved to: {results_file}")

    # Final status
    print_header("PHASE 5 STATUS")

    if total_success == total_tests:
        print("🎉 ALL VALIDATION TESTS PASSED! 🎉")
        print("\nThe PET Rocket Simulator has been successfully verified and validated.")
        print("Ready to proceed to Phase 6: Deployment")
        return 0
    else:
        print(f"⚠️  {total_tests - total_success} test(s) failed")
        print("\nReview failures and address issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
