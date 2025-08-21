"""
Modular NOC Scheduling Algorithm

This module implements a comprehensive employee scheduling system using OR-Tools constraint
programming solver with a modular constraint architecture. Each constraint is implemented
as a separate, maintainable component.

Key Features:
- Multi-shift scheduling (Morning, Evening, Night shifts)
- Ramadan-specific shift patterns
- Holiday and weekend coverage with specific holiday shift labels (HM, HE, HN, HMR, HE1R, HE2R, HNR)
- Expert supervision requirements
- Fair workload distribution
- Vacation balance considerations
- Contiguous shift limitations
- Modular constraint system for easy maintenance and extension

The algorithm uses Google OR-Tools CP-SAT solver to find optimal solutions that satisfy
all specified constraints while maximizing schedule fairness and coverage.
"""
from ortools.sat.python import cp_model
from hijri_converter import convert
import datetime
from datetime import timedelta
from calendar import monthrange
import math
import os
import sys
from typing import List, Dict, Tuple, Optional, Any

# Import utility functions
from .utils import get_all_days, get_specific_month_days, get_weekends, get_ramadan_days, get_day_type, upload_all_holidays

# Import constraint classes
from .constraints import (
    WeekdayShiftsConstraint,
    ExpertSupervisionConstraint,
    EveningNightRestConstraint,
    HolidayShiftsConstraint,
    WeekendShiftsConstraint,
    OneShiftPerDayConstraint,
    FairDistributionConstraint,
    EveningShiftsMinimumConstraint,
    VacationBasedOffDaysConstraint,
    ContiguousShiftsLimitConstraint,
    ShiftsDistributionConstraint,
    OffDayExclusivityConstraint,
)

# Import the solution format solution printer
from .solution_format_printer import SolutionFormatPrinter


class ModularNOCScheduler:
    """
    Comprehensive NOC scheduling system with modular constraint architecture.
    
    This class encapsulates the entire scheduling algorithm, managing employee
    assignments across different shift types while respecting complex constraints
    implemented as separate, maintainable modules.
    
    The scheduler supports multiple shift types:
    - Normal days: Morning (M), Evening (E), Night (N)
    - Ramadan days: Morning Ramadan (MR), Evening 1/2 Ramadan (E1R/E2R), Night Ramadan (NR)
    - Holiday variants with 'H' prefix for all shift types:
      * Normal holidays: HM (Holiday Morning), HE (Holiday Evening), HN (Holiday Night)
      * Ramadan holidays: HMR (Holiday Morning Ramadan), HE1R/HE2R (Holiday Evening Ramadan), HNR (Holiday Night Ramadan)
    
    Key constraint categories (implemented as separate modules):
    - Shift coverage requirements
    - Employee type restrictions (Expert/Beginner)
    - Rest and rotation patterns
    - Fair distribution of workload
    - Vacation balance considerations
    """

    def __init__(self, gregorian_year, gregorian_month, employees_data, holidays_file_path, solution_limit, constraints):
        """
        Initialize the modular NOC scheduler with scheduling parameters and constraints.
        
        Args:
            gregorian_year: Year for scheduling (Gregorian calendar)
            gregorian_month: Month for scheduling (1-12)
            employees_data: List of employee dictionaries with type and vacation info
            holidays_file_path: Path to holidays file or None
            solution_limit: Maximum number of solutions to generate
            constraints: Dictionary of constraint flags, uses defaults if None
        """
        self.gregorian_year = int(gregorian_year)
        self.gregorian_month = int(gregorian_month)
        self.employees_data = employees_data or []
        self.holidays_file_path = holidays_file_path
        self.solution_limit = int(solution_limit) if solution_limit is not None else 1
        
        # Set default constraints if none provided
        if constraints is None:
            constraints = {
                'constraint_weekday_shifts': True,
                'constraint_expert_supervision': True,
                'constraint_e_n_rest': True,
                'constraint_holiday_shifts': True,
                'constraint_weekend_shifts': True,
                'constraint_one_shift_per_person_per_day': True,
                'constraint_fair_weekend_distribution': True,
                'constraint_fair_holiday_distribution': True,
                'constraint_min_normal_evening_shifts': True,
                'constraint_min_abnormal_evening_shifts': True,
                'constraint_evenly_distribute_max_shifts': True,
                'constraint_off_days_based_on_vacation_balance': True,
                'constraint_limit_contiguous_shifts': True
            }
        self.constraints = constraints

        # Initialize data structures (populated during prepare() phase)
        self.hijri_year = None
        self.remaining_months_in_year = None
        self.num_of_team_employees = None
        self.team_employees = None
        self.job_types_remaining_vacation = {}
        self.month_days = []
        self.number_of_month_days = 0
        self.month_indecies = []
        self.all_holidays = []
        self.holidays = []
        self.month_holidays_indecies = []
        self.weekends = []
        self.pure_weekends = []
        self.month_weekends_indecies = []
        self.weekdays = []
        self.month_weekdays_indecies = []
        
        # Shift type definitions
        self.normal_day_shifts = ['N', 'M', 'E']              # Night, Morning, Evening
        self.abnormal_day_shifts = ['MR', 'E1R', 'E2R', 'NR'] # Ramadan variants
        self.abnormal_days = []
        self.abnormal_day_indecies = []
        self.SHIFT_INDICES = {
            'N': 0, 'M': 1, 'E': 2,        # Normal shifts
            'MR': 3, 'E1R': 4, 'E2R': 5, 'NR': 6  # Ramadan shifts
        }
        self.max_shifts_per_employee = None

        # OR-Tools solver and decision variables (initialized in _init_model)
        self.solver = None
        self.weekdays_team_shifts = {}
        self.weekends_team_shifts = {}
        self.holidays_team_shifts = {}
        self.off_days = {}
        self.working_day_vars = {}
        self.rest_day_vars = {}
        
        # Initialize constraint instances
        self._constraint_instances = []

    def prepare(self):
        """
        Prepare all scheduling data including dates, holidays, and employee information.
        
        This method processes the input parameters to create all necessary data
        structures for the scheduling algorithm including date classifications,
        employee type mappings, and calendar calculations.
        """
        # Convert Gregorian date to Hijri year for Ramadan calculations
        self.hijri_year = int(convert.Gregorian(int(self.gregorian_year), 1, 1).to_hijri().year)
        self.remaining_months_in_year = 12 - self.gregorian_month
        self.num_of_team_employees = len(self.employees_data)
        self.team_employees = range(self.num_of_team_employees)

        # Process employee data and create type mappings
        self.job_types_remaining_vacation = {}
        for e, emp_data in enumerate(self.employees_data):
            job_type = emp_data['type'].upper()
            remaining_vacation_days = emp_data['vacation_days']
            if job_type in ['e', 'E', 'EXPERT']:
                self.job_types_remaining_vacation[f'EMPLOYEE_{e}'] = {'type': 'EXPERT', 'vacation_days': remaining_vacation_days}
            elif job_type in ['b', 'B', 'BEGINNER']:
                self.job_types_remaining_vacation[f'EMPLOYEE_{e}'] = {'type': 'BEGINNER', 'vacation_days': remaining_vacation_days}
            else:
                raise ValueError("Invalid employee type.")

        # Generate calendar data for the target month
        self.month_days = get_specific_month_days(self.gregorian_year, self.gregorian_month)
        self.number_of_month_days = len(self.month_days)
        self.month_indecies = range(self.number_of_month_days)

        # Load and process holidays data
        if self.holidays_file_path is not None:
            self.all_holidays = upload_all_holidays(self.gregorian_year, self.holidays_file_path)
        else:
            self.all_holidays = []

        # Filter holidays for the target month
        if self.all_holidays:
            self.holidays = [day for day in self.all_holidays if day.year == self.gregorian_year and day.month == self.gregorian_month]
        else:
            self.holidays = []

        self.month_holidays_indecies = []
        if self.holidays:
            self.holidays = list(set(self.holidays))
            for day in self.holidays:
                if day not in self.month_days:
                    continue
            self.month_holidays_indecies = [self.month_days.index(day) for day in self.holidays]
            self.month_holidays_indecies = list(set(self.month_holidays_indecies))

        self.weekends = get_weekends(self.month_days)
        self.pure_weekends = [day for day in self.weekends if day not in self.holidays]
        self.month_weekends_indecies = [self.month_days.index(day) for day in self.pure_weekends]
        self.weekdays = [day for day in self.month_days if day not in self.weekends and day not in self.holidays]
        self.month_weekdays_indecies = [self.month_days.index(day) for day in self.weekdays]

        ramadan_days, _ = get_ramadan_days(self.hijri_year)
        self.abnormal_days = ramadan_days
        self.abnormal_day_indecies = [self.month_days.index(day) for day in self.abnormal_days if day in self.month_days]

        self.max_shifts_per_employee = len(self.month_indecies) - (len(self.weekends) + len(self.holidays))

    def _init_model(self):
        """
        Initialize the OR-Tools CP model and create all decision variables.
        
        This method sets up the constraint programming model and creates Boolean
        decision variables for all possible shift assignments across weekdays,
        weekends, and holidays. Variables are created based on day type and
        whether it falls during Ramadan (abnormal days).
        """
        self.solver = cp_model.CpModel()
        self.weekdays_team_shifts = {}
        self.weekends_team_shifts = {}
        self.holidays_team_shifts = {}
        self.off_days = {}

        # Create decision variables for weekday shifts
        for employee in self.team_employees:
            for day in self.month_weekdays_indecies:
                if day in self.abnormal_day_indecies:
                    # Ramadan shifts
                    for shift in range(3, 7):
                        self.weekdays_team_shifts[(employee, day, shift)] = self.solver.NewBoolVar(f"weekday_e{employee}_d{day}_s{shift}")
                else:
                    # Normal shifts
                    for shift in range(0, 3):
                        self.weekdays_team_shifts[(employee, day, shift)] = self.solver.NewBoolVar(f"weekday_e{employee}_d{day}_s{shift}")

        # Create decision variables for weekend shifts
        for employee in self.team_employees:
            for day in self.month_weekends_indecies:
                if day in self.abnormal_day_indecies:
                    # Ramadan shifts
                    for shift in range(3, 7):
                        self.weekends_team_shifts[(employee, day, shift)] = self.solver.NewBoolVar(f"weekend_e{employee}_d{day}_s{shift}")
                else:
                    # Normal shifts
                    for shift in range(0, 3):
                        self.weekends_team_shifts[(employee, day, shift)] = self.solver.NewBoolVar(f"weekend_e{employee}_d{day}_s{shift}")

        # Create decision variables for holiday shifts
        if self.holidays and len(self.holidays) > 0:
            for employee in self.team_employees:
                for day in self.month_holidays_indecies:
                    if day in self.abnormal_day_indecies:
                        # Ramadan shifts
                        for shift in range(3, 7):
                            self.holidays_team_shifts[(employee, day, shift)] = self.solver.NewBoolVar(f"holiday_e{employee}_d{day}_s{shift}")
                    else:
                        # Normal shifts
                        for shift in range(0, 3):
                            self.holidays_team_shifts[(employee, day, shift)] = self.solver.NewBoolVar(f"holiday_e{employee}_d{day}_s{shift}")

        # Off days initialization
        for employee in self.team_employees:
            for day_idx in self.month_indecies:
                self.off_days[(employee, day_idx)] = self.solver.NewBoolVar(f"off_e{employee}_d{day_idx}")

    def _initialize_constraints(self):
        """
        Initialize all constraint instances with references to this scheduler.
        
        Creates instances of all constraint classes and stores them for later application.
        This modular approach allows for easy addition, removal, or modification of constraints.
        """
        self._constraint_instances = [
            WeekdayShiftsConstraint(self),
            ExpertSupervisionConstraint(self),
            EveningNightRestConstraint(self),
            HolidayShiftsConstraint(self),
            WeekendShiftsConstraint(self),
            OneShiftPerDayConstraint(self),
            FairDistributionConstraint(self),
            EveningShiftsMinimumConstraint(self),
            VacationBasedOffDaysConstraint(self),
            ContiguousShiftsLimitConstraint(self),
            ShiftsDistributionConstraint(self),
            OffDayExclusivityConstraint(self),
        ]

    def _apply_all_constraints(self):
        """
        Apply all constraints to the scheduling model in the correct order.
        
        This method applies constraints in a specific order to ensure proper
        model construction and to avoid dependency issues between constraints.
        """
        # Get vacation-based off days limits first (needed by shifts distribution)
        vacation_constraint = next(
            (c for c in self._constraint_instances if isinstance(c, VacationBasedOffDaysConstraint)), 
            None
        )
        min_off_days, max_off_days = vacation_constraint.apply() if vacation_constraint else ({}, {})

        # Apply constraints in order
        for constraint in self._constraint_instances:
            if isinstance(constraint, VacationBasedOffDaysConstraint):
                continue  # Already applied above
            elif isinstance(constraint, ShiftsDistributionConstraint):
                # Shifts distribution needs the off days limits
                constraint.apply(min_off_days, max_off_days)
            else:
                constraint.apply()

    def _solve_and_extract(self):
        """
        Solve the constraint programming model and extract results.
        
        This method runs the OR-Tools solver on the constructed model and
        processes the results, generating output files and solution data
        in the same format as the original algorithm.
        """
        # Timestamp format identical to original script pattern
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # File names (parity with original)
        input_summary_name = f"input_summary_{self.gregorian_year}_{self.gregorian_month:02d}_{timestamp_str}.txt"
        off_days_dist_name = f"off_days_distribution_{self.gregorian_year}_{self.gregorian_month:02d}_{timestamp_str}.txt"
        calendar_info_name = f"month_calendar_info_{self.gregorian_year}_{self.gregorian_month:02d}_{timestamp_str}.txt"
        summary_files = [input_summary_name, off_days_dist_name, calendar_info_name]

        # Console header (parity)
        print("Modular NOC Scheduling Algorithm")
        print("=====================================")
        print("Active Scheduling Constraints:")
        for constraint, is_active in self.constraints.items():
            print(f" - {constraint}: {'Enabled' if is_active else 'Disabled'}")

        print("Initialization complete.")
        print(f"Month days: {self.month_days}")
        print(f"Weekdays indices: {self.month_weekdays_indecies}")
        print(f"Weekends indices: {self.month_weekends_indecies}")
        print(f"Holidays indices: {self.month_holidays_indecies}")
        print(f"Month indices: {list(self.month_indecies)}")
        print(f"Ramadan days indices: {self.abnormal_day_indecies}")

        # Calendar info file
        try:
            with open(calendar_info_name, 'w', encoding='utf-8') as f:
                f.write(f"Month Calendar Information for {self.gregorian_year}-{self.gregorian_month:02d}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total days in month: {self.number_of_month_days}\n")
                f.write(f"Weekdays: {len(self.month_weekdays_indecies)}\n")
                f.write(f"Weekends: {len(self.month_weekends_indecies)}\n")
                f.write(f"Holidays: {len(self.month_holidays_indecies)}\n")
                f.write(f"Ramadan days: {len(self.abnormal_day_indecies)}\n\n")
                f.write(f"Weekday indices: {self.month_weekdays_indecies}\n")
                f.write(f"Weekend indices: {self.month_weekends_indecies}\n")
                f.write(f"Holiday indices: {self.month_holidays_indecies}\n")
                f.write(f"Ramadan day indices: {self.abnormal_day_indecies}\n")
        except Exception as e:
            print(f"Error writing calendar info file: {e}")

        # Collector replicating original verbose analytics
        collected_schedule_first: Dict[str, Dict[str, str]] = {}
        solution_files: List[str] = []
        max_shifts_per_employee = self.max_shifts_per_employee

        # Create base filename for solutions
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"solution_{self.gregorian_year}_{self.gregorian_month:02d}_{timestamp_str}"

        # Use the solution format solution printer
        solution_printer = SolutionFormatPrinter(
            self, 
            max(1, int(self.solution_limit)), 
            base_filename, 
            self.constraints
        )

        solver_engine = cp_model.CpSolver()
        solver_engine.parameters.linearization_level = 0
        solver_engine.parameters.max_time_in_seconds = 300.0
        solver_engine.parameters.enumerate_all_solutions = True
        
        status = solver_engine.Solve(self.solver, solution_printer)
        success = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

        # Get the solution files created by the printer
        for i in range(1, solution_printer.get_solution_count() + 1):
            solution_files.append(f"{base_filename}_sol{i}.txt")

        # Get schedule data from the printer
        collected_schedule_first = solution_printer.get_schedule_data()

        # Input summary file
        try:
            with open(input_summary_name, 'w', encoding='utf-8') as f:
                f.write(f"Input Summary for {self.gregorian_year}-{self.gregorian_month:02d}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Number of employees: {self.num_of_team_employees}\n")
                f.write(f"Solution limit: {self.solution_limit}\n")
                f.write(f"Max shifts per employee: {max_shifts_per_employee}\n\n")
                
                f.write("Employee Details:\n")
                f.write("-" * 20 + "\n")
                for emp in self.team_employees:
                    emp_data = self.job_types_remaining_vacation[f'EMPLOYEE_{emp}']
                    f.write(f"Employee {emp + 1}: {emp_data['type']}, {emp_data['vacation_days']} vacation days\n")
                
                f.write("\nActive Constraints:\n")
                f.write("-" * 20 + "\n")
                for constraint, is_active in self.constraints.items():
                    f.write(f"{constraint}: {'Enabled' if is_active else 'Disabled'}\n")
        except Exception as e:
            print(f"Error writing input summary file: {e}")

        # Off days distribution (include min/max)
        try:
            with open(off_days_dist_name, 'w', encoding='utf-8') as f:
                f.write(f"Off Days Distribution for {self.gregorian_year}-{self.gregorian_month:02d}\n")
                f.write("=" * 50 + "\n\n")
                
                for emp in self.team_employees:
                    emp_data = self.job_types_remaining_vacation[f'EMPLOYEE_{emp}']
                    f.write(f"Employee {emp + 1} ({emp_data['type']}):\n")
                    f.write(f"  Remaining vacation days: {emp_data['vacation_days']}\n")
                    f.write(f"  Remaining months in year: {self.remaining_months_in_year}\n")
                    
                    if self.constraints.get('constraint_off_days_based_on_vacation_balance'):
                        if self.remaining_months_in_year == 0:
                            min_off = 1 if emp_data['vacation_days'] >= 1 else 0
                            max_off = emp_data['vacation_days'] if emp_data['vacation_days'] >= 1 else 0
                        else:
                            if emp_data['vacation_days'] >= 1:
                                min_off = emp_data['vacation_days'] // self.remaining_months_in_year
                                max_off = min_off + 1
                            else:
                                min_off = 0
                                max_off = 0
                    else:
                        min_off = 1 if emp_data['vacation_days'] >= 1 else 0
                        max_off = 1 if emp_data['vacation_days'] >= 1 else 0
                    
                    f.write(f"  Min off days this month: {min_off}\n")
                    f.write(f"  Max off days this month: {max_off}\n\n")
        except Exception as e:
            print(f"Error writing off days distribution file: {e}")

        # Append solver status & stats to input summary
        try:
            with open(input_summary_name, 'a', encoding='utf-8') as f:
                f.write(f"\nSolver Results:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Status: {self._get_status_name(status)}\n")
                f.write(f"Solutions found: {solution_printer.get_solution_count()}\n")
                f.write(f"Success: {success}\n")
        except Exception as e:
            print(f"Error appending solver results: {e}")

        print(f"\nResults have been saved to: {input_summary_name}")
        print(f"\nResults have been saved to: {off_days_dist_name}")
        print(f"\nResults have been saved to: {calendar_info_name}")

        output_files = summary_files + solution_files
        error_msg = None
        if not success:
            error_msg = f"Solver failed with status: {self._get_status_name(status)}"

        return success, output_files, status, error_msg, collected_schedule_first, max_shifts_per_employee

    def _get_status_name(self, status_code):
        """
        Convert OR-Tools solver status code to human-readable string.
        
        Args:
            status_code: Integer status code from OR-Tools solver
            
        Returns:
            String representation of the solver status
        """
        if status_code == cp_model.OPTIMAL:
            return "OPTIMAL"
        elif status_code == cp_model.FEASIBLE:
            return "FEASIBLE"
        elif status_code == cp_model.INFEASIBLE:
            return "INFEASIBLE"
        else:
            return f"STATUS_{status_code}"

    def run(self):
        """
        Execute the complete modular scheduling algorithm pipeline.
        
        This method orchestrates the entire scheduling process by:
        1. Preparing all input data and calendar information
        2. Initializing the constraint programming model
        3. Creating constraint instances
        4. Applying all scheduling constraints in sequence
        5. Solving the model and extracting results
        
        Returns:
            Tuple containing (success, output_files, status, error_msg, schedule_data, max_shifts)
        """
        self.prepare()
        self._init_model()
        self._initialize_constraints()
        self._apply_all_constraints()
        return self._solve_and_extract()


def run_modular_scheduling_algorithm(gregorian_year, gregorian_month, employees_data, holidays_file_path, solution_limit, constraints):
    """
    Main entry point for the modular NOC scheduling algorithm.
    
    This function creates a ModularNOCScheduler instance and runs the complete scheduling
    process including data preparation, constraint application, and solution finding.
    
    Args:
        gregorian_year: Year for scheduling
        gregorian_month: Month for scheduling (1-12)
        employees_data: List of employee dictionaries with type and vacation info
        holidays_file_path: Path to holidays file or None
        solution_limit: Maximum number of solutions to generate
        constraints: Dictionary of constraint configuration flags
        
    Returns:
        Tuple containing (success, output_files, status, error_msg, schedule_data, max_shifts)
    """
    scheduler = ModularNOCScheduler(gregorian_year, gregorian_month, employees_data, holidays_file_path, solution_limit, constraints)
    return scheduler.run()


def main():
    """
    Command-line interface for the modular scheduling algorithm.
    
    This function provides a command-line interface for testing purposes.
    It reads scheduling parameters from standard input and executes the
    algorithm, printing results to standard output.
    
    Input format (one per line):
    - Gregorian year
    - Gregorian month
    - Number of employees
    - Employee data pairs (type, vacation_days) for each employee
    - Maximum shifts per employee
    """
    lines = [line.strip() for line in sys.stdin]
    
    try:
        gregorian_year = int(lines[0])
        gregorian_month = int(lines[1])
        num_of_team_employees = int(lines[2])
        
        employees_data = []
        for i in range(num_of_team_employees):
            emp_type = lines[3 + i * 2]
            vacation_days = int(lines[4 + i * 2])
            employees_data.append({'type': emp_type, 'vacation_days': vacation_days})
        
        max_shifts_per_employee = int(lines[3 + num_of_team_employees * 2])

        success, output_files, status, error, schedule_data, max_shifts_per_employee = run_modular_scheduling_algorithm(
            gregorian_year, gregorian_month, employees_data, None, 4, None
        )
        
        if success:
            print("SUCCESS")
            print(f"Files: {','.join(output_files)}")
        else:
            print("FAILED")
            print(f"Error: {error}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
