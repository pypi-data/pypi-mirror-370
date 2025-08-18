"""Hypothesis settings and profiles for the test suite.

This module configures Hypothesis with different profiles for various
testing scenarios (development, CI, debugging).
"""

import os

from hypothesis import HealthCheck, Verbosity, settings

# Define test profiles for different environments

# Development profile - balanced for local development
settings.register_profile(
    "dev",
    max_examples=100,  # Reasonable number for quick feedback
    verbosity=Verbosity.verbose,
    deadline=None,  # Disable deadline to avoid flaky tests in development
    print_blob=True,  # Show reproduction code on failures
    suppress_health_check=[HealthCheck.too_slow],  # Don't fail on slow tests
)

# CI profile - thorough testing for continuous integration
settings.register_profile(
    "ci",
    max_examples=1000,  # More examples for thorough testing
    verbosity=Verbosity.normal,
    deadline=5000,  # 5 seconds deadline
    print_blob=False,  # CI logs are already verbose
    suppress_health_check=[],  # Enable all health checks
    derandomize=True,  # Reproducible test order
)

# Debug profile - minimal examples for debugging
settings.register_profile(
    "debug",
    max_examples=10,  # Very few examples
    verbosity=Verbosity.debug,  # Maximum verbosity
    deadline=None,  # No deadline
    print_blob=True,  # Show reproduction code
    suppress_health_check=[HealthCheck.too_slow],
)

# Quick profile - for pre-commit hooks or quick checks
settings.register_profile(
    "quick",
    max_examples=20,  # Minimal examples
    verbosity=Verbosity.quiet,
    deadline=1000,  # 1 second deadline
    print_blob=False,
    suppress_health_check=[HealthCheck.too_slow],
)

# Performance profile - for finding performance issues
settings.register_profile(
    "performance",
    max_examples=50,
    verbosity=Verbosity.normal,
    deadline=200,  # Very strict deadline (200ms)
    print_blob=True,
    suppress_health_check=[],  # All health checks enabled
)

# Load profile from environment variable, default to 'dev'
current_profile = os.getenv("HYPOTHESIS_PROFILE", "dev")
settings.load_profile(current_profile)

# You can also set a default profile for specific test modules
# by importing this at the top of your test files
