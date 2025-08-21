from dataclasses import dataclass
from typing import Optional
from .point import Point2d, Point3d


@dataclass
class Line2d:
    """A class representing a line in 2D space defined by two points."""
    start: Point2d
    end: Point2d
    
    def __post_init__(self):
        """Validate that start and end points are different."""
        if self.start == self.end:
            raise ValueError("Start and end points cannot be the same")
    
    @property
    def length(self) -> float:
        """Calculate the length of the line."""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        return (dx**2 + dy**2)**0.5
    
    @property
    def midpoint(self) -> Point2d:
        """Calculate the midpoint of the line."""
        return Point2d(
            x=(self.start.x + self.end.x) / 2,
            y=(self.start.y + self.end.y) / 2
        )
    
    def direction_vector(self) -> Point2d:
        """Return the direction vector of the line (not normalized)."""
        return Point2d(
            x=self.end.x - self.start.x,
            y=self.end.y - self.start.y
        )
    
    def unit_direction_vector(self) -> Point2d:
        """Return the unit direction vector of the line."""
        direction = self.direction_vector()
        length = self.length
        if length == 0:
            raise ValueError("Cannot compute unit vector for zero-length line")
        return Point2d(
            x=direction.x / length,
            y=direction.y / length
        )


@dataclass
class Line3d:
    """A class representing a line in 3D space defined by two points."""
    start: Point3d
    end: Point3d
    
    def __post_init__(self):
        """Validate that start and end points are different."""
        if self.start == self.end:
            raise ValueError("Start and end points cannot be the same")
    
    @property
    def length(self) -> float:
        """Calculate the length of the line."""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        dz = self.end.z - self.start.z
        return (dx**2 + dy**2 + dz**2)**0.5
    
    @property
    def midpoint(self) -> Point3d:
        """Calculate the midpoint of the line."""
        return Point3d(
            x=(self.start.x + self.end.x) / 2,
            y=(self.start.y + self.end.y) / 2,
            z=(self.start.z + self.end.z) / 2
        )
    
    def direction_vector(self) -> Point3d:
        """Return the direction vector of the line (not normalized)."""
        return Point3d(
            x=self.end.x - self.start.x,
            y=self.end.y - self.start.y,
            z=self.end.z - self.start.z
        )
    
    def unit_direction_vector(self) -> Point3d:
        """Return the unit direction vector of the line."""
        direction = self.direction_vector()
        length = self.length
        if length == 0:
            raise ValueError("Cannot compute unit vector for zero-length line")
        return Point3d(
            x=direction.x / length,
            y=direction.y / length,
            z=direction.z / length
        )
    
    def project_to_2d(self) -> Line2d | Point2d:
        """Project the 3D line to 2D by dropping the z-coordinate.
        
        Returns:
            Line2d: If the line has a horizontal component
            Point2d: If the line is vertical (appears as a point in plan view)
        """
        start_2d = Point2d(x=self.start.x, y=self.start.y)
        end_2d = Point2d(x=self.end.x, y=self.end.y)
        
        # If the projected points are the same, return the point
        if start_2d == end_2d:
            return start_2d
        
        return Line2d(start=start_2d, end=end_2d)
