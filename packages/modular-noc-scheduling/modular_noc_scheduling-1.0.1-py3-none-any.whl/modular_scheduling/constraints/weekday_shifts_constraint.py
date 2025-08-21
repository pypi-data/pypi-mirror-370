"""
Weekday Shifts Constraint for NOC Scheduling Algorithm.

This module implements constraints for ensuring adequate staffing coverage
on weekdays, with different requirements for normal days versus Ramadan days.
"""

from .base_constraint import BaseConstraint


class WeekdayShiftsConstraint(BaseConstraint):
    """
    Constraint for ensuring adequate shift coverage on weekdays.
    
    This constraint ensures minimum staffing levels for all weekday shifts,
    with different minimum requirements for normal days versus Ramadan days.
    It handles both normal shift types (M, E, N) and Ramadan-specific shifts 
    (MR, E1R, E2R, NR).
    """
    
    def apply(self) -> None:
        """
        Apply weekday shift coverage constraints to the scheduling model.
        
        For normal days:
        - Night (N): minimum 1 employee
        - Morning (M): minimum 2 employees (or 1 if constraint disabled)
        - Evening (E): minimum 1 employee
        
        For Ramadan days:
        - Morning Ramadan (MR): minimum 2 employees (or 1 if constraint disabled)
        - Evening 1 Ramadan (E1R): minimum 1 employee
        - Evening 2 Ramadan (E2R): minimum 1 employee
        - Night Ramadan (NR): minimum 1 employee
        """
        constraint_enabled = self.is_enabled('constraint_weekday_shifts')
        
        for day in self.scheduler.month_weekdays_indecies:
            if day in self.scheduler.abnormal_day_indecies:
                # Ramadan day shifts
                self._apply_ramadan_shifts_constraints(day, constraint_enabled)
            else:
                # Normal day shifts
                self._apply_normal_shifts_constraints(day, constraint_enabled)
    
    def _apply_normal_shifts_constraints(self, day: int, constraint_enabled: bool) -> None:
        """
        Apply constraints for normal weekday shifts.
        
        Args:
            day: The day index
            constraint_enabled: Whether the constraint is enabled (affects minimum staffing)
        """
        shift_indices = self.scheduler.SHIFT_INDICES
        team_employees = self.scheduler.team_employees
        weekdays_shifts = self.scheduler.weekdays_team_shifts
        
        for shift in self.scheduler.normal_day_shifts:
            if shift == 'N':
                # Night shift: minimum 1 employee
                min_employees = 1
            elif shift == 'M':
                # Morning shift: minimum 2 employees if constraint enabled, 1 otherwise
                min_employees = 2 if constraint_enabled else 1
            elif shift == 'E':
                # Evening shift: minimum 1 employee
                min_employees = 1
            else:
                continue
            
            shift_vars = [
                weekdays_shifts[(employee, day, shift_indices[shift])]
                for employee in team_employees
            ]
            self.solver.Add(sum(shift_vars) >= min_employees)
    
    def _apply_ramadan_shifts_constraints(self, day: int, constraint_enabled: bool) -> None:
        """
        Apply constraints for Ramadan weekday shifts.
        
        Args:
            day: The day index
            constraint_enabled: Whether the constraint is enabled (affects minimum staffing)
        """
        shift_indices = self.scheduler.SHIFT_INDICES
        team_employees = self.scheduler.team_employees
        weekdays_shifts = self.scheduler.weekdays_team_shifts
        
        for shift in self.scheduler.abnormal_day_shifts:
            if shift == 'MR':
                # Morning Ramadan: minimum 2 employees if constraint enabled, 1 otherwise
                min_employees = 2 if constraint_enabled else 1
            elif shift in ['E1R', 'E2R', 'NR']:
                # Evening and Night Ramadan shifts: minimum 1 employee
                min_employees = 1
            else:
                continue
            
            shift_vars = [
                weekdays_shifts[(employee, day, shift_indices[shift])]
                for employee in team_employees
            ]
            self.solver.Add(sum(shift_vars) >= min_employees)
