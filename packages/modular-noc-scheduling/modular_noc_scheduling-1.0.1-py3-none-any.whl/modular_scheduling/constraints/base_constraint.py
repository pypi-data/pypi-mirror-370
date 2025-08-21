"""
Base constraint class for NOC Scheduling Algorithm.

This module defines the abstract base class that all constraint implementations
must inherit from. It provides a common interface for applying constraints
to the scheduling model.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseConstraint(ABC):
    """
    Abstract base class for all scheduling constraints.
    
    All constraint implementations must inherit from this class and implement
    the apply() method. This ensures a consistent interface across all constraints
    and allows for easy addition of new constraints.
    """
    
    def __init__(self, scheduler: Any):
        """
        Initialize the constraint with a reference to the scheduler.
        
        Args:
            scheduler: The NOCScheduler instance that contains all the data
                      and decision variables needed for constraint application
        """
        self.scheduler = scheduler
        self.solver = scheduler.solver
        self.constraints_config = scheduler.constraints
    
    @abstractmethod
    def apply(self) -> None:
        """
        Apply this constraint to the scheduling model.
        
        This method must be implemented by all constraint subclasses.
        It should add the appropriate constraints to the solver model
        using the data available in the scheduler.
        """
        pass
    
    def is_enabled(self, constraint_name: str) -> bool:
        """
        Check if a specific constraint is enabled in the configuration.
        
        Args:
            constraint_name: The name of the constraint to check
            
        Returns:
            True if the constraint is enabled, False otherwise
        """
        return self.constraints_config.get(constraint_name, False)
    
    def get_employee_type(self, employee_id: int) -> str:
        """
        Get the type of an employee (EXPERT or BEGINNER).
        
        Args:
            employee_id: The ID of the employee
            
        Returns:
            The employee type as a string
        """
        emp_key = f'EMPLOYEE_{employee_id}'
        return self.scheduler.job_types_remaining_vacation.get(emp_key, {}).get('type', 'BEGINNER')
    
    def is_expert(self, employee_id: int) -> bool:
        """
        Check if an employee is an expert.
        
        Args:
            employee_id: The ID of the employee
            
        Returns:
            True if the employee is an expert, False otherwise
        """
        return self.get_employee_type(employee_id) == 'EXPERT'
    
    def is_beginner(self, employee_id: int) -> bool:
        """
        Check if an employee is a beginner.
        
        Args:
            employee_id: The ID of the employee
            
        Returns:
            True if the employee is a beginner, False otherwise
        """
        return self.get_employee_type(employee_id) == 'BEGINNER'
