from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from simplex.foundation.design.auto_design import DesignSettings, DesignType
from simplex.foundation.model.project_info import ProjectInfo
from simplex.foundation.model.foundation import FoundationBase, RectangularFoundation, LineFoundation
from simplex.foundation.model.reinforcement import Rebars
from simplex.foundation.model.settings import Settings
from simplex.foundation.model.soil import SoilBase
from simplex.foundation.model.foundation_loading import FoundationLoading, PointFoundationLoading, LineFoundationLoading
from simplex.foundation.results import Results
import simplex


@dataclass
class Project:
    project_info: ProjectInfo
    foundation: FoundationBase
    loading: List[FoundationLoading]
    soil: SoilBase
    settings: Settings
    design_settings: DesignSettings = None

    def __post_init__(self):
        """
        Validates the Project object after initialization.
        """
        self._validate_loading()

    def _validate_loading(self):
        """Validates the loading objects based on the type of foundation."""
        if isinstance(self.foundation, RectangularFoundation):
            # Ensure all loading objects are PointFoundationLoading
            if not all(isinstance(load, PointFoundationLoading) for load in self.loading):
                raise ValueError(
                    "For a RectangularFoundation, all loading objects must be of type PointFoundationLoading."
                )

        elif isinstance(self.foundation, LineFoundation):
            # Ensure all loading objects are LineFoundationLoading
            if not all(isinstance(load, LineFoundationLoading) for load in self.loading):
                raise ValueError(
                    "For a LineFoundation, all loading objects must be of type LineFoundationLoading."
                )


    _frontend_proto: 'simplex.core.protos.generated.Frontends.foundation_pb2.Project' = field(default=None, init=False)
    _results: Results = field(default=None, init=False)

    @property
    def results(self):
        if self._results is None:
            raise Exception(
                "Results are not computed. Please run 'run_code_check()' before accessing results."
            )
        return self._results

    @results.setter
    def results(self, value):
        self._results = value

    def run_code_check(self):
         from simplex.foundation.actions import run_code_check
         _code_check_output, _ = run_code_check(self)
         self.results = Results.from_proto(_code_check_output)

    def run_foundation_design(self, design_type: DesignType = DesignType.FOUNDATION_GEOMETRY) -> Tuple[Optional['DesignFoundationResult'], Optional['DesignReinforcementResult']]:
        design_settings = self.design_settings
        design_settings._active = True

        if design_type == DesignType.FOUNDATION_GEOMETRY:
            design_settings.concrete_settings = None
        elif design_type == DesignType.REINFORCEMENT:
            design_settings.foundation_settings = None

        from simplex.foundation.actions import run_foundation_design
        code_check_output, _ = run_foundation_design(self, design_settings)

        from ..results import DesignFoundationResult, DesignReinforcementResult
        foundation_results = DesignFoundationResult.from_proto(code_check_output.project.input)
        concrete_results = DesignReinforcementResult.from_proto(code_check_output.project.input)
        return foundation_results, concrete_results

    def save_as_json(self, filename: str):
        from simplex.foundation.actions import save_as_json
        save_as_json(self, filename)


    @classmethod
    def from_excel(cls, filepath: str) -> 'Project':
        """
        Load a Project from an Excel file.
        
        Args:
            filepath (str): Path to the Excel file
            
        Returns:
            Project: A new Project instance loaded from the Excel file
        """
        from simplex.foundation.actions import load_project_from_excel
        return load_project_from_excel(filepath)