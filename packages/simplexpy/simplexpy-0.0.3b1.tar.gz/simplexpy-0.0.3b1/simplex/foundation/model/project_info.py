from dataclasses import dataclass
from typing import Optional

@dataclass
class ProjectInfo:
    """
    Data class representing metadata and descriptive information for a project.

    Attributes:
        name (str): The name of the project.
        project (Optional[str]): The project code or identifier.
        description (Optional[str]): A description of the project.
        location (Optional[str]): The location where the project is based.
        company (Optional[str]): The company responsible for the project.
        signature (Optional[str]): The signature or initials of the author.
        comments (Optional[str]): Additional comments about the project.
    """
    name: str = ""
    project: Optional[str] = ""
    description: Optional[str] = ""
    location: Optional[str] = ""
    company: Optional[str] = ""
    signature: Optional[str] = ""
    comments: Optional[str] = ""
