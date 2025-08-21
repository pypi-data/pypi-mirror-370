"""
Fair Distribution Constraint for NOC Scheduling Algorithm.

This module implements constraints for ensuring fair distribution of weekend
and holiday shifts among all team members, preventing workload imbalances.
"""

from .base_constraint import BaseConstraint


class FairDistributionConstraint(BaseConstraint):
    """
    Constraint for ensuring fair distribution of weekend and holiday shifts.
    
    This constraint calculates minimum shifts required per employee for
    weekends and holidays, then ensures each employee gets at least their
    fair share of these shifts. This prevents some employees from being
    overloaded with weekend/holiday work while others have none.
    """
    
    def apply(self) -> None:
        """
        Apply fair distribution constraints for weekend and holiday shifts.
        
        Calculates minimum weekend and holiday shifts per employee based on
        total available shifts and team size, then ensures each employee
        gets at least this minimum amount.
        """
        num_employees = self.scheduler.num_of_team_employees
        
        if num_employees > 0:
            min_weekends_per_employee = self._calculate_min_weekend_shifts_per_employee()
            min_holidays_per_employee = self._calculate_min_holiday_shifts_per_employee()
            
            self._apply_fair_weekend_distribution(min_weekends_per_employee)
            self._apply_fair_holiday_distribution(min_holidays_per_employee)
    
    def _calculate_min_weekend_shifts_per_employee(self) -> int:
        """
        Calculate minimum weekend shifts each employee should get.
        
        Returns:
            Minimum weekend shifts per employee based on fair distribution
        """
        num_employees = self.scheduler.num_of_team_employees
        if num_employees == 0:
            return 0
        
        total_weekend_shifts = sum(
            (5 if day in self.scheduler.abnormal_day_indecies else 4)
            for day in self.scheduler.month_weekends_indecies
        )
        
        return total_weekend_shifts // num_employees
    
    def _calculate_min_holiday_shifts_per_employee(self) -> int:
        """
        Calculate minimum holiday shifts each employee should get.
        
        Returns:
            Minimum holiday shifts per employee based on fair distribution
        """
        num_employees = self.scheduler.num_of_team_employees
        if num_employees == 0:
            return 0
        
        total_holiday_shifts = sum(
            (5 if day in self.scheduler.abnormal_day_indecies else 4)
            for day in self.scheduler.month_holidays_indecies
        )
        
        return total_holiday_shifts // num_employees
    
    def _apply_fair_weekend_distribution(self, min_shifts_per_employee: int) -> None:
        """
        Apply fair weekend distribution constraints.
        
        Args:
            min_shifts_per_employee: Minimum weekend shifts each employee should get
        """
        if not self.is_enabled('constraint_fair_weekend_distribution'):
            return
        
        for employee in self.scheduler.team_employees:
            weekend_shift_vars = []
            
            for day in self.scheduler.month_weekends_indecies:
                # Use appropriate shift range based on whether it's a Ramadan day
                shift_range = (
                    range(3, 7) if day in self.scheduler.abnormal_day_indecies 
                    else range(0, 3)
                )
                
                weekend_shift_vars.extend([
                    self.scheduler.weekends_team_shifts[(employee, day, shift)]
                    for shift in shift_range
                ])
            
            if weekend_shift_vars:
                self.solver.Add(sum(weekend_shift_vars) >= min_shifts_per_employee)
    
    def _apply_fair_holiday_distribution(self, min_shifts_per_employee: int) -> None:
        """
        Apply fair holiday distribution constraints.
        
        Args:
            min_shifts_per_employee: Minimum holiday shifts each employee should get
        """
        if not self.is_enabled('constraint_fair_holiday_distribution'):
            return
        
        for employee in self.scheduler.team_employees:
            holiday_shift_vars = []
            
            for day in self.scheduler.month_holidays_indecies:
                # Use appropriate shift range based on whether it's a Ramadan day
                shift_range = (
                    range(3, 7) if day in self.scheduler.abnormal_day_indecies 
                    else range(0, 3)
                )
                
                holiday_shift_vars.extend([
                    self.scheduler.holidays_team_shifts[(employee, day, shift)]
                    for shift in shift_range
                ])
            
            if holiday_shift_vars:
                self.solver.Add(sum(holiday_shift_vars) >= min_shifts_per_employee)
