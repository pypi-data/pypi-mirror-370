"""
Evening-Night Rest Constraint for NOC Scheduling Algorithm.

This module implements constraints for managing rest patterns after evening
and night shift sequences. When an employee works an evening shift, they must
work the night shift the next day and then have a rest day.
"""

from .base_constraint import BaseConstraint


class EveningNightRestConstraint(BaseConstraint):
    """
    Constraint for managing evening-night shift sequences and mandatory rest.
    
    This constraint implements the rule that after an evening shift, an employee
    must work the night shift the next day and then rest the day after that.
    This ensures proper rest patterns and prevents fatigue from consecutive
    evening-night work.
    """
    
    def apply(self) -> None:
        """
        Apply evening-night rest constraints to the scheduling model.
        
        For each employee and each three-day sequence:
        - If employee works evening shift on day 1, they must work night shift on day 2
        - If employee works night shift on day 2, they cannot work any shift on day 3
        
        This only applies to normal (non-Ramadan) days.
        """
        if not self.is_enabled('constraint_e_n_rest'):
            return
        
        month_indices = self.scheduler.month_indecies
        
        for employee in self.scheduler.team_employees:
            for day_idx in range(len(month_indices) - 2):
                current_day = day_idx
                next_day = day_idx + 1
                next_next_day = day_idx + 2
                
                # Only apply to sequences of normal (non-Ramadan) days
                if self._are_all_normal_days([current_day, next_day, next_next_day]):
                    self._apply_e_n_rest_sequence(employee, current_day, next_day, next_next_day)
    
    def _are_all_normal_days(self, days: list) -> bool:
        """
        Check if all days in the sequence are normal (non-Ramadan) days.
        
        Args:
            days: List of day indices to check
            
        Returns:
            True if all days are normal days, False otherwise
        """
        abnormal_days = set(self.scheduler.abnormal_day_indecies)
        return all(day not in abnormal_days for day in days)
    
    def _apply_e_n_rest_sequence(self, employee: int, current_day: int, next_day: int, next_next_day: int) -> None:
        """
        Apply evening-night rest constraints for a specific employee and day sequence.
        
        Args:
            employee: The employee ID
            current_day: First day index
            next_day: Second day index  
            next_next_day: Third day index
        """
        # Get shift variables for the sequence
        e_shift_current = self._get_e_shift_var(employee, current_day)
        n_shift_next = self._get_n_shift_var(employee, next_day)
        all_shifts_next_next = self._get_all_shifts_for_day(employee, next_next_day)
        
        # Apply constraints if all variables exist
        if e_shift_current is not None and n_shift_next is not None and all_shifts_next_next:
            # If evening shift on current day, must work night shift next day
            self.solver.Add(e_shift_current <= n_shift_next)
            
            # If night shift on next day, cannot work any shift the day after
            self.solver.Add(n_shift_next + sum(all_shifts_next_next) <= 1)
    
    def _get_e_shift_var(self, employee: int, day: int):
        """
        Get the evening shift variable for an employee on a specific day.
        
        Args:
            employee: The employee ID
            day: The day index
            
        Returns:
            The evening shift variable or None if not found
        """
        if day in self.scheduler.month_weekdays_indecies:
            return self.scheduler.weekdays_team_shifts[(employee, day, 2)]  # E shift index is 2
        elif day in self.scheduler.month_weekends_indecies:
            return self.scheduler.weekends_team_shifts[(employee, day, 2)]
        elif day in self.scheduler.month_holidays_indecies:
            return self.scheduler.holidays_team_shifts[(employee, day, 2)]
        return None
    
    def _get_n_shift_var(self, employee: int, day: int):
        """
        Get the night shift variable for an employee on a specific day.
        
        Args:
            employee: The employee ID
            day: The day index
            
        Returns:
            The night shift variable or None if not found
        """
        if day in self.scheduler.month_weekdays_indecies:
            return self.scheduler.weekdays_team_shifts[(employee, day, 0)]  # N shift index is 0
        elif day in self.scheduler.month_weekends_indecies:
            return self.scheduler.weekends_team_shifts[(employee, day, 0)]
        elif day in self.scheduler.month_holidays_indecies:
            return self.scheduler.holidays_team_shifts[(employee, day, 0)]
        return None
    
    def _get_all_shifts_for_day(self, employee: int, day: int):
        """
        Get all shift variables for an employee on a specific day.
        
        Args:
            employee: The employee ID
            day: The day index
            
        Returns:
            List of all shift variables for the day or empty list if not found
        """
        if day in self.scheduler.month_weekdays_indecies:
            return [self.scheduler.weekdays_team_shifts[(employee, day, shift)] for shift in range(0, 3)]
        elif day in self.scheduler.month_weekends_indecies:
            return [self.scheduler.weekends_team_shifts[(employee, day, shift)] for shift in range(0, 3)]
        elif day in self.scheduler.month_holidays_indecies:
            return [self.scheduler.holidays_team_shifts[(employee, day, shift)] for shift in range(0, 3)]
        return []
