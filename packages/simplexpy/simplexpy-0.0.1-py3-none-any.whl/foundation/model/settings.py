from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Annex(Enum):
    # ANNEX_UNSPECIFIED = 0
    ANNEX_COMMON = 1            # Standard
    # ANNEX_HUNGARY = 2;      # Hungary
    # ANNEX_ROMANIA = 3;      # Romania
    ANNEX_DENMARK = 4           # Denmark
    ANNEX_SWEDEN = 5            # Sweden
    ANNEX_NORWAY = 6            # Norway
    ANNEX_FINLAND = 7           # Finland
    ANNEX_GREAT_BRITAIN = 8     # UK
    # ANNEX_GERMANY = 9;  // Germany
    # ANNEX_POLAND = 10;  // Poland
    # ANNEX_TURKEY = 11;  // Turkey
    # ANNEX_ESTONIA = 12; // Estonia
    # ANNEX_LATVIA = 13;  // Latvia
    # ANNEX_BELGIUM = 14; // Belgium
    # ANNEX_NETHERLAND = 15;  // Netherland
    # ANNEX_SPAIN = 16;   // Spain

class Consequence(Enum):
    CONSEQUENCE_CLASS_1 = 1 # Consequence class 1 - small or negligible
    CONSEQUENCE_CLASS_2 = 2 # Consequence class 2 - considerable
    CONSEQUENCE_CLASS_3 = 3 # Consequence class 3 - very great

class Reliability(Enum):
    RELIABILITY_CLASS_1 = 1 # Reliability class 1 - (low), minor risk of serious personal injury
    RELIABILITY_CLASS_2 = 2 # Reliability class 2 - (normal), some risk of serious personal injury
    RELIABILITY_CLASS_3 = 3 # Reliability class 3 - (high), major risk of serious personal injury

class FoundationDistribution(Enum):
    FOUNDATION_DISTRIBUTION_ELASTIC = 1   # Plastic distribution of foundation stress
    FOUNDATION_DISTRIBUTION_PLASTIC = 2   # Plastic distribution of foundation stress

class Fabrication(Enum):
    FABRICATION_IN_SITU = 1   # In-situ fabrication
    FABRICATION_PREFAB = 2    # Prefabricated

class Exposure(Enum):
    """Expossure classes related to environmental conditions - EN1992-1-1 4.2"""
    EXPOSURE_CLASS_X0 = 1    # No risk of corrosion or attack
    EXPOSURE_CLASS_XC1 = 2   # Corrosion induced by carbonation : Dry or permanently wet
    EXPOSURE_CLASS_XC2 = 3   # Corrosion induced by carbonation : Wet, rarely dry
    EXPOSURE_CLASS_XC3 = 4   # Corrosion induced by carbonation : Moderate humidity
    EXPOSURE_CLASS_XC4 = 5   # Corrosion induced by carbonation : Cyclic wet and dry
    EXPOSURE_CLASS_XD1 = 6   # Corrosion induced by chlorides: Moderate humidity
    EXPOSURE_CLASS_XD2 = 7   # Corrosion induced by chlorides: Wet, rarely dry
    EXPOSURE_CLASS_XD3 = 8   # Corrosion induced by chlorides: Cyclic wet and dry
    EXPOSURE_CLASS_XS1 = 9   # Corrosion induced by chlorides from sea water : Exposed to airborne salt but not in direct contact with sea water
    EXPOSURE_CLASS_XS2 = 10  # Corrosion induced by chlorides from sea water : Permanently submerged
    EXPOSURE_CLASS_XS3 = 11  # Corrosion induced by chlorides from sea water : Tidal, splash and spray zones
    EXPOSURE_CLASS_XA1 = 12  # Chemical attack : Slightly aggressive
    EXPOSURE_CLASS_XA2 = 13  # Chemical attack : Moderately aggressive
    EXPOSURE_CLASS_XA3 = 14  # Chemical attack : Highly aggressive
    EXPOSURE_CLASS_XF1 = 15  # [NOT USED IN RC DESIGN] Freeze/Thaw Attack : Moderate water saturation, without de-icing agent
    EXPOSURE_CLASS_XF2 = 16  # [NOT USED IN RC DESIGN] Freeze/Thaw Attack : Moderate water saturation, with de-icing agent
    EXPOSURE_CLASS_XF3 = 17  # [NOT USED IN RC DESIGN] Freeze/Thaw Attack : High water saturation, without de-icing agents
    EXPOSURE_CLASS_XF4 = 18  # [NOT USED IN RC DESIGN] Freeze/Thaw Attack : High water saturation with de-icing agents or sea water

class LifeCategory(Enum):
    """Design working life - EN1990-1-1 2.3"""
    LIFE_CATEGORY_L20 = 1    # 20 years
    LIFE_CATEGORY_L50 = 2    # 50 years
    LIFE_CATEGORY_L100 = 3   # 100 years

class DesignApproach(Enum):
    """Design Approach"""
    DESIGN_APPROACH_1 = 1  # design approch 1
    DESIGN_APPROACH_2 = 2  # design approch 2
    DESIGN_APPROACH_3 = 3  # design approch 3

class GeotechnicalCategory(Enum):
    """Geotechnical category"""
    GEOTECHNICAL_CATEGORY_1 = 1  # geotechnical category 1
    GEOTECHNICAL_CATEGORY_2 = 2  # geotechnical category 2
    GEOTECHNICAL_CATEGORY_3 = 3  # geotechnical category 3

class SoilPunchingType(Enum):
    """Type of soil punching"""
    SOIL_PUNCHING_TYPE_WIDTH_1_2 = 1  # Same down to one foundation width, thereafter 1:2
    SOIL_PUNCHING_TYPE_1_2 = 2        # 1:2
    SOIL_PUNCHING_TYPE_1_3 = 3        # 1:3
    SOIL_PUNCHING_TYPE_1_4 = 4        # 1:4

class InspectionLevel(Enum):
    """Inspection level, scope of checking - EC2 Table 2.1N [NA:DK]"""
    INSPECTION_LEVEL_RELAXED = 1        # [DK: Lempet]
    INSPECTION_LEVEL_NORMAL = 2         # [DK: Normal]
    INSPECTION_LEVEL_TIGHTENED = 3      # [DK: Skærpet]


@dataclass
class CodeSettings:
    annex: Optional[Annex] = Annex.ANNEX_COMMON
    consequence: Optional[Consequence] = Consequence.CONSEQUENCE_CLASS_2
    reliability: Optional[Reliability] = Reliability.RELIABILITY_CLASS_1

@dataclass
class ConcreteSettings:
    crack: Optional[float] = 0.001
    distribution: Optional[FoundationDistribution] = FoundationDistribution.FOUNDATION_DISTRIBUTION_PLASTIC
    fabrication: Optional[Fabrication] = Fabrication.FABRICATION_IN_SITU
    low_strength_variation: Optional[bool] = True
    consider_min_reinforcement: Optional[bool] = True
    exposure_class: Optional[Exposure] = Exposure.EXPOSURE_CLASS_XC2
    life_category: Optional[LifeCategory] = LifeCategory.LIFE_CATEGORY_L100

    critical_element: Optional[bool] = True
    inspection_level : Optional[InspectionLevel] = InspectionLevel.INSPECTION_LEVEL_NORMAL

@dataclass
class SoilSettings:
    """
    Represents the soil-related settings for a geotechnical design.

    Attributes:
        des_appr (Optional[DesignApproach]): The design approach to be used. Defaults to DESIGN_APPROACH_3.
        geo_cat (Optional[GeotechnicalCategory]): The geotechnical category. Defaults to GEOTECHNICAL_CATEGORY_2.
        check_settl (Optional[bool]): Whether to check for settlement. Defaults to True.
        abs_sttl (Optional[float]): The absolute settlement limit (in mm). Defaults to 20.
        punching (Optional[SoilPunchingType]): The soil punching type. Defaults to SOIL_PUNCHING_TYPE_1_2.
    """
    des_appr: Optional[DesignApproach] = DesignApproach.DESIGN_APPROACH_3
    geo_cat: Optional[GeotechnicalCategory] = GeotechnicalCategory.GEOTECHNICAL_CATEGORY_2
    check_settl: Optional[bool] = True
    abs_sttl: Optional[float] = 0.02
    punching: Optional[SoilPunchingType] = SoilPunchingType.SOIL_PUNCHING_TYPE_1_2

@dataclass
class Settings:
    code: Optional[CodeSettings] = None
    concrete_sett: Optional[ConcreteSettings] = None
    soil_sett: Optional[SoilSettings] = None