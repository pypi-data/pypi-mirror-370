"""
Modular NOC Scheduling Algorithm Package

This package provides a comprehensive employee scheduling system using OR-Tools constraint
programming solver with a modular constraint architecture. Each constraint is implemented
as a separate, maintainable component.

Key Features:
- Multi-shift scheduling (Morning, Evening, Night shifts)
- Ramadan-specific shift patterns
- Holiday and weekend coverage
- Expert supervision requirements
- Fair workload distribution
- Vacation balance considerations
- Contiguous shift limitations
- Modular constraint system for easy maintenance and extension

Main Components:
- ModularNOCScheduler: Main scheduler class with modular constraint architecture
- constraints: Package containing all constraint implementations
- utils: Utility functions for date calculations and data processing
"""

from .modular_scheduler import ModularNOCScheduler, run_modular_scheduling_algorithm
from .solution_format_printer import SolutionFormatPrinter
from . import constraints
from . import utils

__version__ = "1.0.1"
__author__ = "Innovation Team - Digital Transformation"
__description__ = "Shift Scheduling Algorithm using OR-Tools"

__all__ = [
    'ModularNOCScheduler',
    'run_modular_scheduling_algorithm',
    'SolutionFormatPrinter',
    'constraints',
    'utils',
]
