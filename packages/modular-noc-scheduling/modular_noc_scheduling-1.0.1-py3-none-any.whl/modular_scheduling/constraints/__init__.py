"""
Constraints package for NOC Scheduling Algorithm.

This package contains modular constraint implementations for the scheduling system.
Each constraint is implemented as a separate class that inherits from BaseConstraint.
"""

from .base_constraint import BaseConstraint
from .weekday_shifts_constraint import WeekdayShiftsConstraint
from .expert_supervision_constraint import ExpertSupervisionConstraint
from .evening_night_rest_constraint import EveningNightRestConstraint
from .holiday_shifts_constraint import HolidayShiftsConstraint
from .weekend_shifts_constraint import WeekendShiftsConstraint
from .one_shift_per_day_constraint import OneShiftPerDayConstraint
from .fair_distribution_constraint import FairDistributionConstraint
from .evening_shifts_minimum_constraint import EveningShiftsMinimumConstraint
from .vacation_based_off_days_constraint import VacationBasedOffDaysConstraint
from .contiguous_shifts_limit_constraint import ContiguousShiftsLimitConstraint
from .shifts_distribution_constraint import ShiftsDistributionConstraint
from .off_day_exclusivity_constraint import OffDayExclusivityConstraint

__all__ = [
    'BaseConstraint',
    'WeekdayShiftsConstraint',
    'ExpertSupervisionConstraint',
    'EveningNightRestConstraint',
    'HolidayShiftsConstraint',
    'WeekendShiftsConstraint',
    'OneShiftPerDayConstraint',
    'FairDistributionConstraint',
    'EveningShiftsMinimumConstraint',
    'VacationBasedOffDaysConstraint',
    'ContiguousShiftsLimitConstraint',
    'ShiftsDistributionConstraint',
    'OffDayExclusivityConstraint',
]
