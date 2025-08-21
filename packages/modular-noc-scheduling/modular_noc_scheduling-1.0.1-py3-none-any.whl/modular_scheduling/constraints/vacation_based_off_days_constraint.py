"""
Vacation-Based Off Days Constraint for NOC Scheduling Algorithm.

This module implements constraints for distributing off days based on
employees' remaining vacation balance, ensuring fair vacation usage
throughout the year.
"""

from .base_constraint import BaseConstraint


class VacationBasedOffDaysConstraint(BaseConstraint):
    """
    Constraint for distributing off days based on vacation balance.
    
    This constraint calculates minimum and maximum off days for each employee
    based on their remaining vacation days and the remaining months in the year.
    It ensures that vacation days are distributed fairly across the remaining
    scheduling periods.
    """
    
    def apply(self) -> tuple:
        """
        Apply vacation-based off days constraints and return the calculated limits.
        
        Returns:
            Tuple of (min_off_days_per_month, max_off_days_per_month) dictionaries
        """
        if self.is_enabled('constraint_off_days_based_on_vacation_balance'):
            return self._calculate_vacation_based_off_days()
        else:
            return self._calculate_minimal_off_days()
    
    def _calculate_vacation_based_off_days(self) -> tuple:
        """
        Calculate off days based on vacation balance and remaining months.
        
        Returns:
            Tuple of (min_off_days_per_month, max_off_days_per_month) dictionaries
        """
        min_off_days_per_month = {}
        max_off_days_per_month = {}
        
        for employee in self.scheduler.team_employees:
            employee_data = self._get_employee_vacation_data(employee)
            remaining_vacation_days = employee_data['vacation_days']
            
            if self.scheduler.remaining_months_in_year == 0:
                # Last month of the year - use all remaining vacation
                if remaining_vacation_days >= 1:
                    min_days = 1
                    max_days = remaining_vacation_days
                else:
                    min_days = 0
                    max_days = 0
            else:
                # Distribute vacation across remaining months
                if remaining_vacation_days >= 1:
                    min_days = remaining_vacation_days // self.scheduler.remaining_months_in_year
                    max_days = min_days + 1
                else:
                    min_days = 0
                    max_days = 0
            
            min_off_days_per_month[employee] = min_days
            max_off_days_per_month[employee] = max_days
        
        return min_off_days_per_month, max_off_days_per_month
    
    def _calculate_minimal_off_days(self) -> tuple:
        """
        Calculate minimal off days when vacation-based constraint is disabled.
        
        Returns:
            Tuple of (min_off_days_per_month, max_off_days_per_month) dictionaries
        """
        min_off_days_per_month = {}
        max_off_days_per_month = {}
        
        for employee in self.scheduler.team_employees:
            employee_data = self._get_employee_vacation_data(employee)
            remaining_vacation_days = employee_data['vacation_days']
            
            if remaining_vacation_days >= 1:
                min_days = 1
                max_days = 1
            else:
                min_days = 0
                max_days = 0
            
            min_off_days_per_month[employee] = min_days
            max_off_days_per_month[employee] = max_days
        
        return min_off_days_per_month, max_off_days_per_month
    
    def _get_employee_vacation_data(self, employee: int) -> dict:
        """
        Get vacation data for a specific employee.
        
        Args:
            employee: The employee ID
            
        Returns:
            Dictionary containing employee type and vacation days
        """
        emp_key = f'EMPLOYEE_{employee}'
        return self.scheduler.job_types_remaining_vacation.get(emp_key, {
            'type': 'BEGINNER',
            'vacation_days': 0
        })
