"""
Expert Supervision Constraint for NOC Scheduling Algorithm.

This module implements constraints to ensure that whenever beginner employees
are assigned to shifts, there is at least one expert employee also assigned
to the same shift to provide supervision and guidance.
"""

from .base_constraint import BaseConstraint


class ExpertSupervisionConstraint(BaseConstraint):
    """
    Constraint for ensuring expert supervision when beginners are assigned to shifts.
    
    This constraint guarantees that whenever beginner employees are assigned
    to any shift, there is at least one expert employee also assigned to the
    same shift. This ensures proper supervision and guidance for less experienced
    team members.
    """
    
    def apply(self) -> None:
        """
        Apply expert supervision constraints to the scheduling model.
        
        For each day and shift, the number of beginners assigned cannot exceed
        the number of experts assigned to the same shift.
        """
        if not self.is_enabled('constraint_expert_supervision'):
            return
        
        for day in self.scheduler.month_indecies:
            if day in self.scheduler.abnormal_day_indecies:
                # Ramadan days: use shifts 3-6 (MR, E1R, E2R, NR)
                self._apply_supervision_for_shifts(day, range(3, 7))
            else:
                # Normal days: use shifts 0-2 (N, M, E)
                self._apply_supervision_for_shifts(day, range(0, 3))
    
    def _apply_supervision_for_shifts(self, day: int, shift_range: range) -> None:
        """
        Apply supervision constraints for specific shifts on a given day.
        
        Args:
            day: The day index
            shift_range: Range of shift indices to apply constraints for
        """
        for shift in shift_range:
            shift_vars = self._get_shift_variables(day, shift)
            if shift_vars:
                beginners_vars, experts_vars = shift_vars
                # Number of beginners cannot exceed number of experts
                self.solver.Add(sum(beginners_vars) <= sum(experts_vars))
    
    def _get_shift_variables(self, day: int, shift: int) -> tuple:
        """
        Get the shift variables for beginners and experts for a specific day and shift.
        
        Args:
            day: The day index
            shift: The shift index
            
        Returns:
            Tuple of (beginners_variables, experts_variables) or None if day type not found
        """
        team_employees = self.scheduler.team_employees
        beginners_vars = []
        experts_vars = []
        
        # Determine which shift dictionary to use based on day type
        if day in self.scheduler.month_weekdays_indecies:
            shifts_dict = self.scheduler.weekdays_team_shifts
        elif day in self.scheduler.month_weekends_indecies:
            shifts_dict = self.scheduler.weekends_team_shifts
        elif day in self.scheduler.month_holidays_indecies:
            shifts_dict = self.scheduler.holidays_team_shifts
        else:
            return None
        
        # Collect variables for beginners and experts
        for employee in team_employees:
            shift_var = shifts_dict[(employee, day, shift)]
            if self.is_beginner(employee):
                beginners_vars.append(shift_var)
            elif self.is_expert(employee):
                experts_vars.append(shift_var)
        
        return beginners_vars, experts_vars
