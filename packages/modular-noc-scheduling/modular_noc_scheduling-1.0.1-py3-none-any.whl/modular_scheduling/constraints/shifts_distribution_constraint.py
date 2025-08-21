"""
Shifts Distribution Constraint for NOC Scheduling Algorithm.

This module implements constraints for ensuring even distribution of shifts
among employees, either by enforcing equal maximum shifts or minimum quotas.
"""

from .base_constraint import BaseConstraint


class ShiftsDistributionConstraint(BaseConstraint):
    """
    Constraint for distributing shifts evenly among employees.
    
    This constraint can operate in two modes:
    1. Even distribution: All employees get exactly the same maximum shifts
    2. Minimum distribution: All employees get at least a minimum number of shifts
    
    It also enforces minimum and maximum off days based on vacation balance.
    """
    
    def apply(self, min_off_days_per_month: dict, max_off_days_per_month: dict) -> None:
        """
        Apply shifts distribution constraints to the scheduling model.
        
        Args:
            min_off_days_per_month: Minimum off days for each employee
            max_off_days_per_month: Maximum off days for each employee
        """
        if self.is_enabled('constraint_evenly_distribute_max_shifts'):
            self._apply_even_distribution()
        else:
            self._apply_minimum_distribution()
        
        self._apply_off_days_limits(min_off_days_per_month, max_off_days_per_month)
    
    def _apply_even_distribution(self) -> None:
        """
        Apply even distribution constraint - all employees get equal maximum shifts.
        
        This ensures that all employees have the same total workload by setting
        their shift count plus off days to equal the maximum shifts per employee.
        """
        for employee in self.scheduler.team_employees:
            shift_variables = self._collect_all_shift_variables(employee)
            off_day_variables = [
                self.scheduler.off_days[(employee, day_idx)]
                for day_idx in self.scheduler.month_indecies
            ]
            
            # Total shifts + off days = max shifts per employee
            self.solver.Add(
                sum(shift_variables) + sum(off_day_variables) == 
                self.scheduler.max_shifts_per_employee
            )
    
    def _apply_minimum_distribution(self) -> None:
        """
        Apply minimum distribution constraint - all employees get at least minimum shifts.
        
        This calculates a minimum number of shifts each employee should get based
        on total shift requirements and team size, then ensures each employee
        meets this minimum.
        """
        total_needed_shifts = self._calculate_total_needed_shifts()
        min_shifts_per_employee = (
            total_needed_shifts // self.scheduler.num_of_team_employees
            if self.scheduler.num_of_team_employees > 0 else 0
        )
        
        for employee in self.scheduler.team_employees:
            shift_vars = self._collect_all_shift_variables(employee)
            off_day_variables = [
                self.scheduler.off_days[(employee, day_idx)]
                for day_idx in self.scheduler.month_indecies
            ]
            
            # Total shifts + off days >= minimum required
            self.solver.Add(
                sum(shift_vars) + sum(off_day_variables) >= min_shifts_per_employee
            )
    
    def _calculate_total_needed_shifts(self) -> int:
        """
        Calculate total number of shifts needed across all day types.
        
        Returns:
            Total shifts required for the month
        """
        total_shifts = 0
        
        # Count weekday shifts
        for day_idx in self.scheduler.month_weekdays_indecies:
            if day_idx in self.scheduler.abnormal_day_indecies:
                total_shifts += 5  # Ramadan weekday shifts
            else:
                total_shifts += 4  # Normal weekday shifts
        
        # Count weekend shifts
        for day_idx in self.scheduler.month_weekends_indecies:
            if day_idx in self.scheduler.abnormal_day_indecies:
                total_shifts += 5  # Ramadan weekend shifts
            else:
                total_shifts += 4  # Normal weekend shifts
        
        # Count holiday shifts
        for day_idx in self.scheduler.month_holidays_indecies:
            if day_idx in self.scheduler.abnormal_day_indecies:
                total_shifts += 5  # Ramadan holiday shifts
            else:
                total_shifts += 4  # Normal holiday shifts
        
        return total_shifts
    
    def _collect_all_shift_variables(self, employee: int) -> list:
        """
        Collect all shift variables for an employee across all days and day types.
        
        Args:
            employee: The employee ID
            
        Returns:
            List of all shift variables for the employee
        """
        shift_variables = []
        
        for day_idx in self.scheduler.month_indecies:
            # Determine shift range based on day type
            if day_idx in self.scheduler.abnormal_day_indecies:
                shift_range = range(3, 7)  # Ramadan shifts
            else:
                shift_range = range(0, 3)  # Normal shifts
            
            # Collect from appropriate day type
            if day_idx in self.scheduler.month_weekdays_indecies:
                shift_variables.extend([
                    self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]
                    for shift in shift_range
                ])
            elif day_idx in self.scheduler.month_weekends_indecies:
                shift_variables.extend([
                    self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]
                    for shift in shift_range
                ])
            elif day_idx in self.scheduler.month_holidays_indecies:
                shift_variables.extend([
                    self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]
                    for shift in shift_range
                ])
        
        return shift_variables
    
    def _apply_off_days_limits(self, min_off_days_per_month: dict, max_off_days_per_month: dict) -> None:
        """
        Apply minimum and maximum off days constraints for each employee.
        
        Args:
            min_off_days_per_month: Minimum off days for each employee
            max_off_days_per_month: Maximum off days for each employee
        """
        for employee in self.scheduler.team_employees:
            min_days = min_off_days_per_month.get(employee, 0)
            max_days = max_off_days_per_month.get(employee, 0)
            
            off_day_vars = [
                self.scheduler.off_days[(employee, day_idx)]
                for day_idx in self.scheduler.month_indecies
            ]
            
            # Apply minimum and maximum off days constraints
            self.solver.Add(sum(off_day_vars) >= min_days)
            self.solver.Add(sum(off_day_vars) <= max_days)
