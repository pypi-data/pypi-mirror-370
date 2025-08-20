from dataclasses import dataclass
from typing import List, Optional
from orionis.support.entities.base import BaseEntity

@dataclass(kw_only=True)
class Task(BaseEntity):
    """
    Represents a task entity containing metadata for execution and description.

    Parameters
    ----------
    signature : str
        The unique identifier or signature of the task.
    args : Optional[List[str]], optional
        List of arguments required by the task, by default None.
    purpose : str, optional
        Brief description of the task's purpose, by default None.
    trigger : str, optional
        Event or condition that triggers the task, by default None.
    details : str, optional
        Additional details or information about the task, by default None.

    Returns
    -------
    Task
        An instance of the Task class with the specified metadata.
    """

    # Unique identifier for the task
    signature: str

    # List of arguments required by the task (optional)
    args: Optional[List[str]] = None

    # Brief description of the task's purpose (optional)
    purpose: str = None

    # Event or condition that triggers the task (optional)
    trigger: str = None

    # Additional details or information about the task (optional)
    details: str = None