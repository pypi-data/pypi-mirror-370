"""
Contiguous Shifts Limit Constraint for NOC Scheduling Algorithm.

This module implements constraints to limit the number of consecutive
working days for employees, ensuring proper rest periods and work-life balance.
"""

import math
from .base_constraint import BaseConstraint


class ContiguousShiftsLimitConstraint(BaseConstraint):
    """
    Constraint for limiting contiguous (consecutive) working shifts.
    
    This constraint prevents employees from working too many consecutive days
    by calculating an appropriate window size based on the total workload and
    available rest periods, then ensuring no employee works more than the
    allowed consecutive days within any rolling window.
    """
    
    def apply(self) -> None:
        """
        Apply contiguous shifts limit constraints to the scheduling model.
        
        Creates working day variables and applies rolling window constraints
        to limit consecutive working periods based on the calculated maximum
        contiguous shifts size.
        """
        if not self.is_enabled('constraint_limit_contiguous_shifts'):
            return
        
        contiguous_shifts_size = self._calculate_contiguous_shifts_size()
        self._create_working_day_variables()
        self._apply_contiguous_limits(contiguous_shifts_size)
    
    def _calculate_contiguous_shifts_size(self) -> int:
        """
        Calculate the maximum allowed contiguous shifts based on workload distribution.
        
        Returns:
            Maximum number of consecutive working days allowed
        """
        number_of_month_weekends = len(self.scheduler.pure_weekends) + len(self.scheduler.holidays)
        
        if number_of_month_weekends == 0:
            return 0
        
        return math.ceil(self.scheduler.max_shifts_per_employee / number_of_month_weekends)
    
    def _create_working_day_variables(self) -> None:
        """
        Create Boolean variables to track whether an employee is working on each day.
        
        These variables are used to simplify the contiguous shifts constraints
        by abstracting away the specific shift types and focusing on whether
        the employee is working or not.
        """
        self.scheduler.working_day_vars = {}
        
        for employee in self.scheduler.team_employees:
            for day_idx in self.scheduler.month_indecies:
                # Create working day variable
                working_var = self.solver.NewBoolVar(f"working_e{employee}_d{day_idx}")
                self.scheduler.working_day_vars[(employee, day_idx)] = working_var
                
                # Get all shift variables for this employee and day
                all_shifts_this_day = self._get_all_shifts_for_day(employee, day_idx)
                
                if all_shifts_this_day:
                    # Working day variable is true if any shift is assigned
                    for shift_var in all_shifts_this_day:
                        self.solver.Add(working_var >= shift_var)
                    self.solver.Add(working_var <= sum(all_shifts_this_day))
                else:
                    # No shifts available for this day
                    self.solver.Add(working_var == 0)
    
    def _get_all_shifts_for_day(self, employee: int, day_idx: int) -> list:
        """
        Get all possible shift variables for an employee on a specific day.
        
        Args:
            employee: The employee ID
            day_idx: The day index
            
        Returns:
            List of all shift variables for the employee on the given day
        """
        all_shifts = []
        
        # Determine shift range based on whether it's a Ramadan day
        if day_idx in self.scheduler.abnormal_day_indecies:
            shift_range = range(3, 7)  # Ramadan shifts
        else:
            shift_range = range(0, 3)  # Normal shifts
        
        # Collect shifts from appropriate day type
        if day_idx in self.scheduler.month_weekdays_indecies:
            all_shifts.extend([
                self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]
                for shift in shift_range
            ])
        elif day_idx in self.scheduler.month_weekends_indecies:
            all_shifts.extend([
                self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]
                for shift in shift_range
            ])
        elif day_idx in self.scheduler.month_holidays_indecies:
            all_shifts.extend([
                self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]
                for shift in shift_range
            ])
        
        return all_shifts
    
    def _apply_contiguous_limits(self, contiguous_shifts_size: int) -> None:
        """
        Apply rolling window constraints to limit consecutive working days.
        
        Args:
            contiguous_shifts_size: Maximum allowed consecutive working days
        """
        month_indices = list(self.scheduler.month_indecies)
        
        for employee in self.scheduler.team_employees:
            if len(month_indices) > contiguous_shifts_size:
                # Apply rolling window constraint
                for start_day in range(len(month_indices) - contiguous_shifts_size):
                    working_days_in_window = []
                    
                    # Collect working day variables for the window
                    for i in range(contiguous_shifts_size + 1):
                        day_idx = month_indices[start_day + i]
                        working_days_in_window.append(
                            self.scheduler.working_day_vars[(employee, day_idx)]
                        )
                    
                    # Ensure at most 'contiguous_shifts_size' working days in window
                    self.solver.Add(sum(working_days_in_window) <= contiguous_shifts_size)
