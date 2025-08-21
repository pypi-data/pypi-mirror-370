"""
Off Day Exclusivity Constraint for NOC Scheduling Algorithm.

This module implements constraints to ensure proper handling of off days
and rest day patterns, preventing conflicts between shifts and off time.
"""

from .base_constraint import BaseConstraint


class OffDayExclusivityConstraint(BaseConstraint):
    """
    Constraint for managing off day exclusivity and rest day patterns.
    
    This constraint ensures that:
    1. Employees cannot be both OFF and assigned to shifts on the same day
    2. Rest days following Evening-Night sequences are properly managed
    3. Proper labeling variables are created for rest day tracking
    """
    
    def apply(self) -> None:
        """
        Apply off day exclusivity and rest day constraints to the scheduling model.
        
        Ensures that off days are mutually exclusive with shift assignments
        and manages mandatory rest days following evening-night sequences.
        """
        self._apply_off_day_exclusivity()
        self._apply_rest_day_patterns()
    
    def _apply_off_day_exclusivity(self) -> None:
        """
        Ensure off days are mutually exclusive with shift assignments.
        
        For each employee and day, ensure they cannot be both OFF and
        assigned to any shift on the same day.
        """
        for employee in self.scheduler.team_employees:
            for day_idx in self.scheduler.month_indecies:
                shift_vars = self._get_all_shift_vars_for_day(employee, day_idx)
                
                if shift_vars:
                    # Off day + any shift assignment <= 1 (mutually exclusive)
                    self.solver.Add(
                        self.scheduler.off_days[(employee, day_idx)] + sum(shift_vars) <= 1
                    )
    
    def _apply_rest_day_patterns(self) -> None:
        """
        Apply rest day patterns for evening-night sequences.
        
        Creates rest day variables and ensures that after an evening-night
        sequence, employees cannot be assigned to off days during mandatory rest.
        """
        if not self.is_enabled('constraint_e_n_rest'):
            return
        
        # Initialize rest day variables if not exists
        if not hasattr(self.scheduler, 'rest_day_vars'):
            self.scheduler.rest_day_vars = {}
        
        for employee in self.scheduler.team_employees:
            for day_idx in self.scheduler.month_indecies:
                if day_idx >= 2:
                    self._apply_rest_sequence_constraint(employee, day_idx)
    
    def _apply_rest_sequence_constraint(self, employee: int, day_idx: int) -> None:
        """
        Apply rest sequence constraint for a specific employee and day.
        
        Args:
            employee: The employee ID
            day_idx: The current day index (must be >= 2 for sequence check)
        """
        prev_prev = day_idx - 2
        prev = day_idx - 1
        
        # Only apply to sequences of normal (non-Ramadan) days
        if self._are_all_normal_days([prev_prev, prev, day_idx]):
            e_var = self._get_e_shift_var(employee, prev_prev)
            n_var = self._get_n_shift_var(employee, prev)
            
            if e_var is not None and n_var is not None:
                # Create rest day variable
                rest_var = self.solver.NewBoolVar(f"rest_day_e{employee}_d{day_idx}")
                
                # Rest day is true if both evening and night shifts are worked
                self.solver.Add(rest_var >= e_var + n_var - 1)
                self.solver.Add(rest_var <= e_var)
                self.solver.Add(rest_var <= n_var)
                
                # Cannot be OFF if mandatory rest day
                self.solver.Add(
                    self.scheduler.off_days[(employee, day_idx)] + rest_var <= 1
                )
                
                self.scheduler.rest_day_vars[(employee, day_idx)] = rest_var
    
    def _get_all_shift_vars_for_day(self, employee: int, day_idx: int) -> list:
        """
        Get all shift variables for an employee on a specific day.
        
        Args:
            employee: The employee ID
            day_idx: The day index
            
        Returns:
            List of all shift variables for the employee on the given day
        """
        shift_vars = []
        
        # Determine shift range based on day type
        if day_idx in self.scheduler.abnormal_day_indecies:
            shift_range = range(3, 7)  # Ramadan shifts
        else:
            shift_range = range(0, 3)  # Normal shifts
        
        # Collect from appropriate day type
        if day_idx in self.scheduler.month_weekdays_indecies:
            shift_vars.extend([
                self.scheduler.weekdays_team_shifts[(employee, day_idx, s)]
                for s in shift_range
            ])
        elif day_idx in self.scheduler.month_weekends_indecies:
            shift_vars.extend([
                self.scheduler.weekends_team_shifts[(employee, day_idx, s)]
                for s in shift_range
            ])
        elif day_idx in self.scheduler.month_holidays_indecies:
            shift_vars.extend([
                self.scheduler.holidays_team_shifts[(employee, day_idx, s)]
                for s in shift_range
            ])
        
        return shift_vars
    
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
