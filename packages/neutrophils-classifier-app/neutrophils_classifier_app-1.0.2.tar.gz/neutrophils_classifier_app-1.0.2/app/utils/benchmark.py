"""
Benchmarking utilities for performance monitoring.
"""
import time

# Global benchmark state
_benchmark_start_time = time.time()
_benchmark_times = {}


def log_benchmark(phase_name):
    """Log timing benchmark for a specific phase"""
    current_time = time.time()
    elapsed = current_time - _benchmark_start_time
    if phase_name in _benchmark_times:
        phase_duration = elapsed - _benchmark_times[phase_name]['start']
        _benchmark_times[phase_name]['duration'] = phase_duration
        print(f"BENCHMARK [{phase_name}] COMPLETED: {phase_duration:.3f}s (total: {elapsed:.3f}s)")
    else:
        _benchmark_times[phase_name] = {'start': elapsed}
        print(f"BENCHMARK [{phase_name}] STARTED at {elapsed:.3f}s")


def print_benchmark_summary():
    """Print a summary of all timing benchmarks"""
    total_time = time.time() - _benchmark_start_time
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)
    for phase, times in _benchmark_times.items():
        if 'duration' in times:
            percentage = (times['duration'] / total_time) * 100
            print(f"  {phase:<25}: {times['duration']:>8.3f}s ({percentage:>5.1f}%)")
    print(f"  {'TOTAL APPLICATION STARTUP':<25}: {total_time:>8.3f}s (100.0%)")
    print("="*60 + "\n")


def reset_benchmark():
    """Reset benchmark timer and clear all recorded times"""
    global _benchmark_start_time, _benchmark_times
    _benchmark_start_time = time.time()
    _benchmark_times = {}