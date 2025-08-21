"""
    Solution printer that formats the solution output file.
    This module provides a detailed solution printer that creates output files
    with the same format as the solution NOC scheduling implementation.
"""

import datetime
from typing import Dict, List, Any
from ortools.sat.python import cp_model


class SolutionFormatPrinter(cp_model.CpSolverSolutionCallback):
    """
    Solution printer that formats the solution output file.
    
    This class creates detailed solution files with the same structure, content, and
    formatting as the solution implementation, including:
    - Detailed daily breakdown with day types
    - Employee summaries with shift counts
    - Shift type distribution
    - Overall team statistics
    - Coverage analysis
    """
    
    def __init__(self, scheduler_instance, max_solutions, base_filename, constraints=None):
        """
        Initialize the solution printer.
        
        Args:
            scheduler_instance: The ModularNOCScheduler instance
            max_solutions: Maximum number of solutions to capture
            base_filename: Base filename for solution files
            constraints: Dictionary of constraint flags
        """
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.scheduler = scheduler_instance
        self.max_solutions = max_solutions
        self.base_filename = base_filename
        self.solution_count = 0
        self.constraints = constraints or {}
        
        # Store the best schedule for UI
        self._best_schedule = {}
        
        # Helper mappings
        self.normal_day_shifts = ['N', 'M', 'E']
        self.abnormal_day_shifts = ['MR', 'E1R', 'E2R', 'NR']
        
    def on_solution_callback(self):
        """Called when a new solution is found."""
        self.solution_count += 1
        solution_filename = f"{self.base_filename}_sol{self.solution_count}.txt"
        
        try:
            with open(solution_filename, "w", encoding="utf-8") as f:
                self._write_solution_to_file(f)
            print(f"Solution {self.solution_count} saved to: {solution_filename}")
        except Exception as e:
            print(f"Error writing solution file: {e}")
        
        # Extract schedule data for UI (only for the first solution)
        if self.solution_count == 1:
            self._extract_schedule_data()
        
        if self.solution_count >= self.max_solutions:
            print(f"Stop search after {self.max_solutions} solutions")
            self.StopSearch()
    
    def _write_solution_to_file(self, f):
        """Write the detailed solution to file in solution format."""
        f.write(f"Solution {self.solution_count}:\n")
        f.write("=====================================\n")
        
        # Calculate solution statistics
        total_shifts, total_off_days = 0, 0
        weekend_shifts, holiday_shifts, ramadan_shifts = 0, 0, 0
        shifts_per_employee = {emp: 0 for emp in self.scheduler.team_employees}
        off_days_per_employee = {emp: 0 for emp in self.scheduler.team_employees}
        
        # Count shifts and off days
        for employee in self.scheduler.team_employees:
            for day_idx in self.scheduler.month_indecies:
                # Count off days
                if self.Value(self.scheduler.off_days[(employee, day_idx)]) == 1:
                    off_days_per_employee[employee] += 1
                    total_off_days += 1
                
                # Count shifts by day type
                if day_idx in self.scheduler.month_weekdays_indecies:
                    if day_idx in self.scheduler.abnormal_day_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shifts_per_employee[employee] += 1
                                    total_shifts += 1
                                    ramadan_shifts += 1
                    else:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shifts_per_employee[employee] += 1
                                    total_shifts += 1
                
                elif day_idx in self.scheduler.month_weekends_indecies:
                    if day_idx in self.scheduler.abnormal_day_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shifts_per_employee[employee] += 1
                                    total_shifts += 1
                                    weekend_shifts += 1
                                    ramadan_shifts += 1
                    else:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shifts_per_employee[employee] += 1
                                    total_shifts += 1
                                    weekend_shifts += 1
                
                elif day_idx in self.scheduler.month_holidays_indecies:
                    if day_idx in self.scheduler.abnormal_day_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shifts_per_employee[employee] += 1
                                    total_shifts += 1
                                    holiday_shifts += 1
                                    ramadan_shifts += 1
                    else:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shifts_per_employee[employee] += 1
                                    total_shifts += 1
                                    holiday_shifts += 1
        
        # Display solution status and summary
        f.write("SOLUTION STATUS AND SUMMARY:\n")
        f.write(f"  Total Shifts: {total_shifts}\n")
        f.write(f"  Total Off Days: {total_off_days}\n")
        f.write(f"  Weekend Shifts: {weekend_shifts}\n")
        f.write(f"  Holiday Shifts: {holiday_shifts}\n")
        f.write(f"  Ramadan Shifts: {ramadan_shifts}\n")
        
        # Shift distribution fairness
        min_shifts = min(shifts_per_employee.values())
        max_shifts = max(shifts_per_employee.values())
        shift_variance = max_shifts - min_shifts
        f.write(f"  Shift Distribution: Min={min_shifts}, Max={max_shifts}, Variance={shift_variance}\n")
        
        # Off days distribution
        min_off_days = min(off_days_per_employee.values())
        max_off_days = max(off_days_per_employee.values())
        off_days_variance = max_off_days - min_off_days
        f.write(f"  Off Days Distribution: Min={min_off_days}, Max={max_off_days}, Variance={off_days_variance}\n")
        
        f.write("-------------------------------------\n")
        f.write("Detailed shifts for the month (including holidays and Ramadan):\n")
        
        # Detailed daily breakdown
        for day_idx in self.scheduler.month_indecies:
            day = self.scheduler.month_days[day_idx]
            day_type = self._get_day_type(day)
            
            # Print day type and date
            if day_idx in self.scheduler.abnormal_day_indecies:
                f.write(f"Day {day_idx} ({day.strftime('%Y-%m-%d')}): RAMADAN\n")
            else:
                f.write(f"Day {day_idx} ({day.strftime('%Y-%m-%d')}): {day_type}\n")
            
            for employee in self.scheduler.team_employees:
                shift_worked = None
                shift_label = None
                emp_type = self.scheduler.job_types_remaining_vacation[f'EMPLOYEE_{employee}']['type']
                
                if day_idx in self.scheduler.abnormal_day_indecies:
                    # Ramadan day: use abnormal shifts
                    if day_idx in self.scheduler.month_weekdays_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.abnormal_day_shifts[shift - 3]
                                    shift_label = shift_worked
                    elif day_idx in self.scheduler.month_weekends_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.abnormal_day_shifts[shift - 3]
                                    shift_label = shift_worked
                    elif day_idx in self.scheduler.month_holidays_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.abnormal_day_shifts[shift - 3]
                                    # Map holiday Ramadan shifts to HMR, HE1R, HE2R, HNR
                                    if shift_worked == 'MR':
                                        shift_label = 'HMR'
                                    elif shift_worked == 'E1R':
                                        shift_label = 'HE1R'
                                    elif shift_worked == 'E2R':
                                        shift_label = 'HE2R'
                                    elif shift_worked == 'NR':
                                        shift_label = 'HNR'
                else:
                    # Normal day
                    if day_idx in self.scheduler.month_weekdays_indecies:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.normal_day_shifts[shift]
                                    shift_label = shift_worked
                    elif day_idx in self.scheduler.month_weekends_indecies:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.normal_day_shifts[shift]
                                    shift_label = shift_worked
                    elif day_idx in self.scheduler.month_holidays_indecies:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.normal_day_shifts[shift]
                                    # Map holiday shifts to HM, HN, HE
                                    if shift_worked == 'M':
                                        shift_label = 'HM'
                                    elif shift_worked == 'N':
                                        shift_label = 'HN'
                                    elif shift_worked == 'E':
                                        shift_label = 'HE'
                
                if self.Value(self.scheduler.off_days[(employee, day_idx)]) == 1:
                    f.write(f"  Employee {employee} [{emp_type}]: OFF\n")
                elif shift_label:
                    f.write(f"  Employee {employee} [{emp_type}]: {shift_label} shift\n")
                else:
                    # Check if this is a Rest day (E->N->OFF pattern)
                    is_rest_day = self._check_rest_day(employee, day_idx)
                    
                    # Only show "Rest" if the E-N-Rest constraint is enabled
                    if is_rest_day and self.constraints.get('constraint_e_n_rest', False):
                        f.write(f"  Employee {employee} [{emp_type}]: No shift assigned - Rest\n")
                    else:
                        f.write(f"  Employee {employee} [{emp_type}]: No shift assigned\n")
            
            f.write("-------------------------------------\n")
        
        # Employee summaries
        self._write_employee_summaries(f, shifts_per_employee, off_days_per_employee)
        
        # Overall team statistics
        self._write_team_statistics(f, shifts_per_employee, off_days_per_employee)
    
    def _get_day_type(self, day):
        """Get the type of day (HOLIDAY, WEEKEND, WEEKDAY)."""
        if day in self.scheduler.holidays:
            return 'HOLIDAY'
        elif day.weekday() == 4 or day.weekday() == 5:  # Friday or Saturday
            return 'WEEKEND'
        else:
            return 'WEEKDAY'
    
    def _check_rest_day(self, employee, day_idx):
        """Check if the current day is a mandatory rest day (E->N->Rest pattern)."""
        if day_idx < 2:  # Need at least 2 previous days
            return False
        
        prev_prev_day = day_idx - 2
        prev_day = day_idx - 1
        
        # Check if all three days are not abnormal
        if (prev_prev_day in self.scheduler.abnormal_day_indecies or 
            prev_day in self.scheduler.abnormal_day_indecies or 
            day_idx in self.scheduler.abnormal_day_indecies):
            return False
        
        # Check E shift on day-2
        had_e_shift = False
        if prev_prev_day in self.scheduler.month_weekdays_indecies:
            if (employee, prev_prev_day, 2) in self.scheduler.weekdays_team_shifts:
                had_e_shift = self.Value(self.scheduler.weekdays_team_shifts[(employee, prev_prev_day, 2)]) == 1
        elif prev_prev_day in self.scheduler.month_weekends_indecies:
            if (employee, prev_prev_day, 2) in self.scheduler.weekends_team_shifts:
                had_e_shift = self.Value(self.scheduler.weekends_team_shifts[(employee, prev_prev_day, 2)]) == 1
        elif prev_prev_day in self.scheduler.month_holidays_indecies:
            if (employee, prev_prev_day, 2) in self.scheduler.holidays_team_shifts:
                had_e_shift = self.Value(self.scheduler.holidays_team_shifts[(employee, prev_prev_day, 2)]) == 1
        
        # Check N shift on day-1
        had_n_shift = False
        if prev_day in self.scheduler.month_weekdays_indecies:
            if (employee, prev_day, 0) in self.scheduler.weekdays_team_shifts:
                had_n_shift = self.Value(self.scheduler.weekdays_team_shifts[(employee, prev_day, 0)]) == 1
        elif prev_day in self.scheduler.month_weekends_indecies:
            if (employee, prev_day, 0) in self.scheduler.weekends_team_shifts:
                had_n_shift = self.Value(self.scheduler.weekends_team_shifts[(employee, prev_day, 0)]) == 1
        elif prev_day in self.scheduler.month_holidays_indecies:
            if (employee, prev_day, 0) in self.scheduler.holidays_team_shifts:
                had_n_shift = self.Value(self.scheduler.holidays_team_shifts[(employee, prev_day, 0)]) == 1
        
        return had_e_shift and had_n_shift
    
    def _write_employee_summaries(self, f, shifts_per_employee, off_days_per_employee):
        """Write detailed employee summaries."""
        f.write("=====================================\n")
        f.write("EMPLOYEE SUMMARY:\n")
        
        for employee in self.scheduler.team_employees:
            emp_type = self.scheduler.job_types_remaining_vacation[f'EMPLOYEE_{employee}']['type']
            f.write(f"Employee {employee} [{emp_type}] :\n")
            
            employee_shifts = []
            for day_idx in self.scheduler.month_indecies:
                day = self.scheduler.month_days[day_idx]
                shift_label = None
                
                if day_idx in self.scheduler.abnormal_day_indecies:
                    # Ramadan day
                    if day_idx in self.scheduler.month_weekdays_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.abnormal_day_shifts[shift - 3]
                                    shift_label = shift_worked
                    elif day_idx in self.scheduler.month_weekends_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.abnormal_day_shifts[shift - 3]
                                    shift_label = shift_worked
                    elif day_idx in self.scheduler.month_holidays_indecies:
                        for shift in range(3, 7):
                            if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.abnormal_day_shifts[shift - 3]
                                    if shift_worked == 'MR':
                                        shift_label = 'HMR'
                                    elif shift_worked == 'E1R':
                                        shift_label = 'HE1R'
                                    elif shift_worked == 'E2R':
                                        shift_label = 'HE2R'
                                    elif shift_worked == 'NR':
                                        shift_label = 'HNR'
                else:
                    # Normal day
                    if day_idx in self.scheduler.month_weekdays_indecies:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_label = self.normal_day_shifts[shift]
                    elif day_idx in self.scheduler.month_weekends_indecies:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_label = self.normal_day_shifts[shift]
                    elif day_idx in self.scheduler.month_holidays_indecies:
                        for shift in range(0, 3):
                            if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                    shift_worked = self.normal_day_shifts[shift]
                                    if shift_worked == 'M':
                                        shift_label = 'HM'
                                    elif shift_worked == 'N':
                                        shift_label = 'HN'
                                    elif shift_worked == 'E':
                                        shift_label = 'HE'
                
                if shift_label:
                    employee_shifts.append(f"Day {day_idx} ({day.strftime('%Y-%m-%d')}): {shift_label}")
                elif self.Value(self.scheduler.off_days[(employee, day_idx)]) == 1:
                    employee_shifts.append(f"Day {day_idx} ({day.strftime('%Y-%m-%d')}): OFF")
                else:
                    # Check if this is a Rest day
                    is_rest_day = self._check_rest_day(employee, day_idx)
                    
                    if is_rest_day and self.constraints.get('constraint_e_n_rest', False):
                        employee_shifts.append(f"Day {day_idx} ({day.strftime('%Y-%m-%d')}): No shift assigned - Rest")
                    else:
                        employee_shifts.append(f"Day {day_idx} ({day.strftime('%Y-%m-%d')}): No shift assigned")
            
            # Display employee shifts
            for shift_info in employee_shifts:
                f.write(f"  {shift_info}\n")
            
            # Employee statistics
            f.write(f"  Total shifts: {shifts_per_employee[employee]}\n")
            f.write(f"  Total off days: {off_days_per_employee[employee]}\n")
            f.write("-------------------------------------\n")
    
    def _write_team_statistics(self, f, shifts_per_employee, off_days_per_employee):
        """Write overall team statistics with detailed breakdown."""
        f.write("=====================================\n")
        f.write("OVERALL TEAM STATISTICS:\n")
        f.write(f"Total Employees: {len(self.scheduler.team_employees)}\n")
        
        for employee in self.scheduler.team_employees:
            emp_type = self.scheduler.job_types_remaining_vacation[f'EMPLOYEE_{employee}']['type']
            f.write(f"Employee {employee} [{emp_type}] - Shifts: {shifts_per_employee[employee]}, Off Days: {off_days_per_employee[employee]}\n")
            
            total_shift = shifts_per_employee[employee] + off_days_per_employee[employee]
            extra_shifts = total_shift - self.scheduler.max_shifts_per_employee
            if self.scheduler.max_shifts_per_employee <= total_shift:
                f.write(f"(Extra Shifts: {extra_shifts})\n")
            else:
                f.write(f"(Extra Shifts: 0)\n")
            
            f.write("." * 20 + "\n")
            
            # Weekend shifts per employee
            for day in self.scheduler.month_weekends_indecies:
                if day in self.scheduler.abnormal_day_indecies:
                    # Abnormal
                    for shift in range(3, 7):
                        if (employee, day, shift) in self.scheduler.weekends_team_shifts:
                            if self.Value(self.scheduler.weekends_team_shifts[(employee, day, shift)]) == 1:
                                f.write(f"  Employee {employee} - Weekends {day} (Abnormal): Shift {shift} = {self.abnormal_day_shifts[shift - 3]}\n")
                else:
                    # Normal
                    for shift in range(0, 3):
                        if (employee, day, shift) in self.scheduler.weekends_team_shifts:
                            if self.Value(self.scheduler.weekends_team_shifts[(employee, day, shift)]) == 1:
                                f.write(f"  Employee {employee} - Weekends {day}: Shift {shift} = {self.normal_day_shifts[shift]}\n")
            
            f.write("." * 20 + "\n")
            
            # Holiday shifts per employee
            for day in self.scheduler.month_holidays_indecies:
                if day in self.scheduler.abnormal_day_indecies:
                    # Abnormal
                    for shift in range(3, 7):
                        if (employee, day, shift) in self.scheduler.holidays_team_shifts:
                            if self.Value(self.scheduler.holidays_team_shifts[(employee, day, shift)]) == 1:
                                f.write(f"  Employee {employee} - Holidays {day} (Abnormal): Shift {shift} = H{self.abnormal_day_shifts[shift - 3]}\n")
                else:
                    # Normal
                    for shift in range(0, 3):
                        if (employee, day, shift) in self.scheduler.holidays_team_shifts:
                            if self.Value(self.scheduler.holidays_team_shifts[(employee, day, shift)]) == 1:
                                f.write(f"  Employee {employee} - Holidays {day}: Shift {shift} = H{self.normal_day_shifts[shift]}\n")
            
            # Shift Type Distribution
            f.write("Shift Type Distribution:\n")
            
            # Count normal shifts (M, E, N)
            normal_shift_counts = {shift: 0 for shift in self.normal_day_shifts}
            for day in self.scheduler.month_indecies:
                if day in self.scheduler.abnormal_day_indecies:
                    continue
                for shift_idx, shift in enumerate(self.normal_day_shifts):
                    if day in self.scheduler.month_weekdays_indecies:
                        if (employee, day, shift_idx) in self.scheduler.weekdays_team_shifts:
                            if self.Value(self.scheduler.weekdays_team_shifts[(employee, day, shift_idx)]) == 1:
                                normal_shift_counts[shift] += 1
                    elif day in self.scheduler.month_weekends_indecies:
                        if (employee, day, shift_idx) in self.scheduler.weekends_team_shifts:
                            if self.Value(self.scheduler.weekends_team_shifts[(employee, day, shift_idx)]) == 1:
                                normal_shift_counts[shift] += 1
                    elif day in self.scheduler.month_holidays_indecies:
                        if (employee, day, shift_idx) in self.scheduler.holidays_team_shifts:
                            if self.Value(self.scheduler.holidays_team_shifts[(employee, day, shift_idx)]) == 1:
                                normal_shift_counts[shift] += 1
            
            # Count abnormal shifts (MR, E1R, E2R, NR)
            abnormal_shift_counts = {shift: 0 for shift in self.abnormal_day_shifts}
            for day in self.scheduler.abnormal_day_indecies:
                for shift_idx, shift in enumerate(self.abnormal_day_shifts):
                    if day in self.scheduler.month_weekdays_indecies:
                        if (employee, day, shift_idx + 3) in self.scheduler.weekdays_team_shifts:
                            if self.Value(self.scheduler.weekdays_team_shifts[(employee, day, shift_idx + 3)]) == 1:
                                abnormal_shift_counts[shift] += 1
                    elif day in self.scheduler.month_weekends_indecies:
                        if (employee, day, shift_idx + 3) in self.scheduler.weekends_team_shifts:
                            if self.Value(self.scheduler.weekends_team_shifts[(employee, day, shift_idx + 3)]) == 1:
                                abnormal_shift_counts[shift] += 1
                    elif day in self.scheduler.month_holidays_indecies:
                        if (employee, day, shift_idx + 3) in self.scheduler.holidays_team_shifts:
                            if self.Value(self.scheduler.holidays_team_shifts[(employee, day, shift_idx + 3)]) == 1:
                                abnormal_shift_counts[shift] += 1
            
            f.write(f"  Normal Shifts: M: {normal_shift_counts['M']}, E: {normal_shift_counts['E']}, N: {normal_shift_counts['N']}\n")
            f.write(f"  Abnormal Shifts: MR: {abnormal_shift_counts['MR']}, E1R: {abnormal_shift_counts['E1R']}, E2R: {abnormal_shift_counts['E2R']}, NR: {abnormal_shift_counts['NR']}\n")
            f.write("=====================================\n")
    
    def _extract_schedule_data(self):
        """Extract schedule data for UI display (matching solution format)."""
        schedule_data = {}
        
        # Initialize schedule data structure
        for employee in self.scheduler.team_employees:
            schedule_data[f'Employee {employee + 1}'] = {}  # Convert to 1-based indexing
            
            for day_idx in self.scheduler.month_indecies:
                day = self.scheduler.month_days[day_idx]
                day_key = f'Day {day_idx + 1} ({day.strftime("%Y-%m-%d")})'  # Convert to 1-based indexing
                # Find what shift this employee is working on this day
                shift_label = None
                is_off_day = self.Value(self.scheduler.off_days[(employee, day_idx)]) == 1
                
                if is_off_day:
                    shift_label = 'OFF'
                else:
                    # Check for shifts based on day type
                    if day_idx in self.scheduler.abnormal_day_indecies:
                        # Ramadan day: use abnormal shifts
                        if day_idx in self.scheduler.month_weekdays_indecies:
                            for shift in range(3, 7):
                                if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                    if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                        shift_label = self.abnormal_day_shifts[shift - 3]
                                        break
                        elif day_idx in self.scheduler.month_weekends_indecies:
                            for shift in range(3, 7):
                                if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                    if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                        shift_label = self.abnormal_day_shifts[shift - 3]
                                        break
                        elif day_idx in self.scheduler.month_holidays_indecies:
                            for shift in range(3, 7):
                                if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                    if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                        shift_worked = self.abnormal_day_shifts[shift - 3]
                                        # Map holiday Ramadan shifts
                                        if shift_worked == 'MR':
                                            shift_label = 'HMR'
                                        elif shift_worked == 'E1R':
                                            shift_label = 'HE1R'
                                        elif shift_worked == 'E2R':
                                            shift_label = 'HE2R'
                                        elif shift_worked == 'NR':
                                            shift_label = 'HNR'
                                        break
                    else:
                        # Normal day: use normal shifts
                        if day_idx in self.scheduler.month_weekdays_indecies:
                            for shift in range(0, 3):
                                if (employee, day_idx, shift) in self.scheduler.weekdays_team_shifts:
                                    if self.Value(self.scheduler.weekdays_team_shifts[(employee, day_idx, shift)]) == 1:
                                        shift_label = self.normal_day_shifts[shift]
                                        break
                        elif day_idx in self.scheduler.month_weekends_indecies:
                            for shift in range(0, 3):
                                if (employee, day_idx, shift) in self.scheduler.weekends_team_shifts:
                                    if self.Value(self.scheduler.weekends_team_shifts[(employee, day_idx, shift)]) == 1:
                                        shift_label = self.normal_day_shifts[shift]
                                        break
                        elif day_idx in self.scheduler.month_holidays_indecies:
                            for shift in range(0, 3):
                                if (employee, day_idx, shift) in self.scheduler.holidays_team_shifts:
                                    if self.Value(self.scheduler.holidays_team_shifts[(employee, day_idx, shift)]) == 1:
                                        shift_worked = self.normal_day_shifts[shift]
                                        # Map holiday shifts
                                        if shift_worked == 'M':
                                            shift_label = 'HM'
                                        elif shift_worked == 'N':
                                            shift_label = 'HN'
                                        elif shift_worked == 'E':
                                            shift_label = 'HE'
                                        break
                    
                    # If no shift found, check if it's a mandatory rest day
                    if not shift_label:
                        is_rest_day = self._check_rest_day(employee, day_idx)
                        
                        # Only show "Rest" if the E-N-Rest constraint is enabled
                        if is_rest_day and self.constraints.get('constraint_e_n_rest', False):
                            shift_label = 'No Shift Assigned - Rest'
                        else:
                            shift_label = 'No Shift Assigned'
                
                schedule_data[f'Employee {employee + 1}'][day_key] = shift_label or 'No Shift Assigned'  # Convert to 1-based indexing
        
        self._best_schedule = schedule_data
    
    def get_schedule_data(self):
        """Return the extracted schedule data for UI."""
        return self._best_schedule
    
    def get_solution_count(self):
        """Return the number of solutions found."""
        return self.solution_count
