"""
Evening Shifts Minimum Constraint for NOC Scheduling Algorithm.

This module implements constraints to ensure fair distribution of evening shifts
among employees, both for normal days and Ramadan days.
"""

from .base_constraint import BaseConstraint


class EveningShiftsMinimumConstraint(BaseConstraint):
    """
    Constraint for ensuring minimum evening shifts distribution.
    
    This constraint ensures that evening shifts are fairly distributed among
    employees by setting minimum requirements for both normal evening shifts
    and Ramadan evening shifts (E1R and E2R).
    """
    
    def apply(self) -> None:
        """
        Apply minimum evening shifts constraints to the scheduling model.
        
        Applies separate minimum requirements for:
        1. Normal evening shifts on non-Ramadan days
        2. Ramadan evening shifts (E1R and E2R) on Ramadan days
        """
        self._apply_normal_evening_shifts_minimum()
        self._apply_ramadan_evening_shifts_minimum()
    
    def _apply_normal_evening_shifts_minimum(self) -> None:
        """
        Apply minimum normal evening shifts constraint.
        
        Ensures each employee gets a fair share of evening shifts on normal days.
        """
        if not self.is_enabled('constraint_min_normal_evening_shifts'):
            return
        
        # Get all normal (non-Ramadan) days
        normal_days = [
            day for day in self.scheduler.month_indecies 
            if day not in self.scheduler.abnormal_day_indecies
        ]
        
        num_employees = self.scheduler.num_of_team_employees
        min_evening_shifts_per_employee = (
            len(normal_days) // num_employees if num_employees > 0 else 0
        )
        
        for employee in self.scheduler.team_employees:
            evening_shift_vars = self._collect_normal_evening_shifts(employee, normal_days)
            if evening_shift_vars:
                self.solver.Add(sum(evening_shift_vars) >= min_evening_shifts_per_employee)
    
    def _apply_ramadan_evening_shifts_minimum(self) -> None:
        """
        Apply minimum Ramadan evening shifts constraint.
        
        Ensures each employee gets a fair share of both E1R and E2R shifts
        during Ramadan days.
        """
        if not self.is_enabled('constraint_min_abnormal_evening_shifts'):
            return
        
        if len(self.scheduler.abnormal_day_indecies) == 0:
            return
        
        num_employees = self.scheduler.num_of_team_employees
        min_evening_shifts_per_employee = (
            len(self.scheduler.abnormal_day_indecies) // num_employees 
            if num_employees > 0 else 0
        )
        
        for employee in self.scheduler.team_employees:
            # Apply constraint for E1R shifts (shift index 4)
            e1r_shift_vars = self._collect_ramadan_evening_shifts(employee, 4)
            if e1r_shift_vars:
                self.solver.Add(sum(e1r_shift_vars) >= min_evening_shifts_per_employee)
            
            # Apply constraint for E2R shifts (shift index 5)
            e2r_shift_vars = self._collect_ramadan_evening_shifts(employee, 5)
            if e2r_shift_vars:
                self.solver.Add(sum(e2r_shift_vars) >= min_evening_shifts_per_employee)
    
    def _collect_normal_evening_shifts(self, employee: int, normal_days: list) -> list:
        """
        Collect all normal evening shift variables for an employee.
        
        Args:
            employee: The employee ID
            normal_days: List of normal (non-Ramadan) day indices
            
        Returns:
            List of evening shift variables for the employee on normal days
        """
        evening_shifts = []
        evening_shift_index = 2  # E shift index
        
        for day in normal_days:
            if day in self.scheduler.month_weekdays_indecies:
                evening_shifts.append(
                    self.scheduler.weekdays_team_shifts[(employee, day, evening_shift_index)]
                )
            elif day in self.scheduler.month_weekends_indecies:
                evening_shifts.append(
                    self.scheduler.weekends_team_shifts[(employee, day, evening_shift_index)]
                )
            elif day in self.scheduler.month_holidays_indecies:
                evening_shifts.append(
                    self.scheduler.holidays_team_shifts[(employee, day, evening_shift_index)]
                )
        
        return evening_shifts
    
    def _collect_ramadan_evening_shifts(self, employee: int, shift_index: int) -> list:
        """
        Collect Ramadan evening shift variables for an employee.
        
        Args:
            employee: The employee ID
            shift_index: The shift index (4 for E1R, 5 for E2R)
            
        Returns:
            List of Ramadan evening shift variables for the employee
        """
        evening_shifts = []
        
        for day in self.scheduler.abnormal_day_indecies:
            if day in self.scheduler.month_weekdays_indecies:
                evening_shifts.append(
                    self.scheduler.weekdays_team_shifts[(employee, day, shift_index)]
                )
            elif day in self.scheduler.month_weekends_indecies:
                evening_shifts.append(
                    self.scheduler.weekends_team_shifts[(employee, day, shift_index)]
                )
            elif day in self.scheduler.month_holidays_indecies:
                evening_shifts.append(
                    self.scheduler.holidays_team_shifts[(employee, day, shift_index)]
                )
        
        return evening_shifts
