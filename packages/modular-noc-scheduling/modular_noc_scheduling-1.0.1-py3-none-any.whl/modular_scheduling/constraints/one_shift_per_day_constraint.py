"""
One Shift Per Day Constraint for NOC Scheduling Algorithm.

This module implements constraints to ensure that each employee is assigned
to at most one shift per day across all day types (weekdays, weekends, holidays).
"""

from .base_constraint import BaseConstraint


class OneShiftPerDayConstraint(BaseConstraint):
    """
    Constraint for ensuring each employee has at most one shift per day.
    
    This constraint prevents employees from being assigned to multiple shifts
    on the same day, ensuring proper work-life balance and preventing scheduling
    conflicts. It applies across all day types and shift categories.
    """
    
    def apply(self) -> None:
        """
        Apply one shift per day constraints to the scheduling model.
        
        For each employee and each day, ensure they are assigned to at most
        one shift regardless of the day type (weekday, weekend, holiday) or
        shift category (normal, Ramadan).
        """
        if not self.is_enabled('constraint_one_shift_per_person_per_day'):
            return
        
        for employee in self.scheduler.team_employees:
            for day in self.scheduler.month_indecies:
                shift_vars = self._collect_all_shift_vars(employee, day)
                if shift_vars:
                    # Use OR-Tools helper to ensure at most one shift is assigned
                    self.solver.AddAtMostOne(shift_vars)
    
    def _collect_all_shift_vars(self, employee: int, day: int) -> list:
        """
        Collect all possible shift variables for an employee on a specific day.
        
        This method gathers shift variables from all applicable day types
        (weekdays, weekends, holidays) and shift categories (normal, Ramadan)
        for a given employee and day.
        
        Args:
            employee: The employee ID
            day: The day index
            
        Returns:
            List of all applicable shift variables for the employee-day combination
        """
        shift_vars = []
        
        # Determine shift range based on whether it's a Ramadan day
        if day in self.scheduler.abnormal_day_indecies:
            shift_range = range(3, 7)  # Ramadan shifts: MR, E1R, E2R, NR
        else:
            shift_range = range(0, 3)  # Normal shifts: N, M, E
        
        # Collect variables from weekdays
        if day in self.scheduler.month_weekdays_indecies:
            shift_vars.extend([
                self.scheduler.weekdays_team_shifts[(employee, day, shift)]
                for shift in shift_range
            ])
        
        # Collect variables from weekends
        if day in self.scheduler.month_weekends_indecies:
            shift_vars.extend([
                self.scheduler.weekends_team_shifts[(employee, day, shift)]
                for shift in shift_range
            ])
        
        # Collect variables from holidays
        if day in self.scheduler.month_holidays_indecies:
            shift_vars.extend([
                self.scheduler.holidays_team_shifts[(employee, day, shift)]
                for shift in shift_range
            ])
        
        return shift_vars
