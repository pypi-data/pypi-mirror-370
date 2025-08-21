"""
Holiday Shifts Constraint for NOC Scheduling Algorithm.

This module implements constraints for ensuring adequate staffing coverage
on holidays, with exact staffing requirements for different shift types.
"""

from .base_constraint import BaseConstraint


class HolidayShiftsConstraint(BaseConstraint):
    """
    Constraint for ensuring exact shift coverage on holidays.
    
    This constraint ensures exact staffing levels for all holiday shifts,
    with different requirements for normal holidays versus Ramadan holidays.
    It handles both normal shift types (M, E, N) and Ramadan-specific shifts 
    (MR, E1R, E2R, NR).
    """
    
    def apply(self) -> None:
        """
        Apply holiday shift coverage constraints to the scheduling model.
        
        For normal holidays:
        - Night (N): exactly 1 employee
        - Morning (M): exactly 2 employees (or 1 if constraint disabled)
        - Evening (E): exactly 1 employee
        
        For Ramadan holidays:
        - Morning Ramadan (MR): exactly 2 employees (or 1 if constraint disabled)
        - Evening 1 Ramadan (E1R): exactly 1 employee
        - Evening 2 Ramadan (E2R): exactly 1 employee
        - Night Ramadan (NR): exactly 1 employee
        """
        constraint_enabled = self.is_enabled('constraint_holiday_shifts')
        
        for day in self.scheduler.month_holidays_indecies:
            if day in self.scheduler.abnormal_day_indecies:
                # Ramadan holiday shifts
                self._apply_ramadan_holiday_shifts_constraints(day, constraint_enabled)
            else:
                # Normal holiday shifts
                self._apply_normal_holiday_shifts_constraints(day, constraint_enabled)
    
    def _apply_normal_holiday_shifts_constraints(self, day: int, constraint_enabled: bool) -> None:
        """
        Apply constraints for normal holiday shifts.
        
        Args:
            day: The day index
            constraint_enabled: Whether the constraint is enabled (affects staffing requirements)
        """
        shift_indices = self.scheduler.SHIFT_INDICES
        team_employees = self.scheduler.team_employees
        holidays_shifts = self.scheduler.holidays_team_shifts
        
        for shift in self.scheduler.normal_day_shifts:
            if shift == 'N':
                # Night shift: exactly 1 employee
                required_employees = 1
            elif shift == 'M':
                # Morning shift: exactly 2 employees if constraint enabled, 1 otherwise
                required_employees = 2 if constraint_enabled else 1
            elif shift == 'E':
                # Evening shift: exactly 1 employee
                required_employees = 1
            else:
                continue
            
            shift_vars = [
                holidays_shifts[(employee, day, shift_indices[shift])]
                for employee in team_employees
            ]
            self.solver.Add(sum(shift_vars) == required_employees)
    
    def _apply_ramadan_holiday_shifts_constraints(self, day: int, constraint_enabled: bool) -> None:
        """
        Apply constraints for Ramadan holiday shifts.
        
        Args:
            day: The day index
            constraint_enabled: Whether the constraint is enabled (affects staffing requirements)
        """
        shift_indices = self.scheduler.SHIFT_INDICES
        team_employees = self.scheduler.team_employees
        holidays_shifts = self.scheduler.holidays_team_shifts
        
        for shift in self.scheduler.abnormal_day_shifts:
            if shift == 'MR':
                # Morning Ramadan: exactly 2 employees if constraint enabled, 1 otherwise
                required_employees = 2 if constraint_enabled else 1
            elif shift in ['E1R', 'E2R', 'NR']:
                # Evening and Night Ramadan shifts: exactly 1 employee
                required_employees = 1
            else:
                continue
            
            shift_vars = [
                holidays_shifts[(employee, day, shift_indices[shift])]
                for employee in team_employees
            ]
            self.solver.Add(sum(shift_vars) == required_employees)
