# Foundation module - simplified imports for user convenience

# Core foundation classes
from .model.project_info import ProjectInfo
from .model.foundation import RectangularFoundation, LineFoundation
from .model.foundation_loading import PointFoundationLoading, LineFoundationLoading, LoadType
from .model.soil import SoilMaterial, Borehole, SoilComplex, SoilSimple
from .model.reinforcement import ReinfLayer, Rebars, Zone
from .model.settings import (
    Settings, CodeSettings, ConcreteSettings, SoilSettings,
    Annex, Consequence, Reliability, FoundationDistribution, Fabrication,
    Exposure, LifeCategory, DesignApproach, GeotechnicalCategory, 
    SoilPunchingType, InspectionLevel
)
from .model.project import Project

# Design classes
from .design.auto_design import (
    DesignSettings, FoundationDesign, ConcreteDesign, Interval, DesignType
)

# Results
from .results import Direction

# Re-export commonly used classes for convenience
__all__ = [
    # Core classes
    'ProjectInfo',
    'RectangularFoundation', 
    'LineFoundation',
    'PointFoundationLoading',
    'LineFoundationLoading',
    'LoadType',
    'SoilMaterial',
    'Borehole',
    'SoilComplex',
    'SoilSimple',
    'ReinfLayer',
    'Rebars',
    'Zone',
    'Settings',
    'CodeSettings',
    'ConcreteSettings',
    'SoilSettings',
    'Project',
    
    # Design classes
    'DesignSettings',
    'FoundationDesign',
    'ConcreteDesign',
    'Interval',
    'DesignType',
    
    # Enums
    'Annex',
    'Consequence',
    'Reliability',
    'FoundationDistribution',
    'Fabrication',
    'Exposure',
    'LifeCategory',
    'DesignApproach',
    'GeotechnicalCategory',
    'SoilPunchingType',
    'InspectionLevel',
    
    # Results
    'Direction'
]
