from collections import namedtuple
import simplex.foundation.design.auto_design
import simplex.foundation.design
import simplex.core
import simplex.core.actions
import simplex.core.actions.IO
from simplex.core.actions.analysis import run_analysis as core_run_analysis
from simplex.core.actions.analysis import update_gamma as core_update_gamma
from simplex.core.actions.IO import save_json  as core_save_as_json
import simplex.core.auth 
import simplex.core.auth.device_flow
import simplex.core.config
import simplex.core.config.endpoints
import simplex.core.converters
import simplex.core.converters.foundation_converter
import simplex.core.protos
import simplex.core.protos.generated
import simplex.core.protos.generated.EndPointArguments
import simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2
from simplex.core.protos.generated.Frontends import foundation_pb2
import simplex
import simplex.foundation
import simplex.foundation.model
import simplex.foundation.model.project
from enum import Enum
from typing import List
from simplex.foundation.excel_reader import _read_project_info_from_excel, _read_foundation_loading_from_excel, _read_reinforcement_from_excel, _read_foundation_from_excel, _read_settings_from_excel, _read_soil_from_excel, _read_design_settings_from_excel

token = simplex.core.auth.device_flow.get_access_token()

def run_code_check(project : simplex.foundation.model.project.Project):

    proto = _update_gamma(project)

    url = simplex.core.config.endpoints.Endpoints.foundation.rc_control.url
    code_check_input = simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.CodeCheckInput(project=proto.data,
                                                                                            lcomb_guids=[],
                                                                                            mathml=False,
                                                                                            mathmlmax=False)


    json_proto = simplex.core.actions.IO.message_to_json(code_check_input)
    return ( core_run_analysis(url, json_proto, token), proto )

def _update_gamma(project : simplex.foundation.model.project.Project) -> foundation_pb2.Project:
    url = simplex.core.config.endpoints.Endpoints.eurocode.update_gammas.url
    frontend_proto = simplex.core.converters.foundation_converter.convert_to_frontend_project_proto(project)

    json_proto = simplex.core.actions.IO.message_to_json(frontend_proto.data)
    proto_data = core_update_gamma(url, json_proto, token)

    frontend_proto.data.CopyFrom(proto_data)

    return frontend_proto


def run_foundation_design(project : simplex.foundation.model.project.Project, design_settings : simplex.foundation.design.auto_design.DesignSettings):

    url = simplex.core.config.endpoints.Endpoints.foundation.geo_design.url

    if design_settings.concrete_settings is not None:
        url = simplex.core.config.endpoints.Endpoints.foundation.rc_design.url

    frontend_proto = _update_gamma(project)
    proto_design = frontend_proto.settings.endpoint_cache.auto_design

    code_check_input = simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.CodeCheckInput(project=frontend_proto.data,
                                                                                            lcomb_guids=[],
                                                                                            mathml=False,
                                                                                            mathmlmax=False,
                                                                                            auto_design=proto_design)


    json_proto = simplex.core.actions.IO.message_to_json(code_check_input)
    return ( core_run_analysis(url, json_proto, token), frontend_proto )

def save_as_json(project: simplex.foundation.model.project.Project, filename: str):
    """
    Save the project proto to a JSON file.
    """
    project_proto = _update_gamma(project)
    core_save_as_json(project_proto, filename)

def load_project_from_excel(filepath: str) -> simplex.foundation.model.project.Project:
    """
    Load a Project from an Excel file.
    
    Args:
        filepath (str): Path to the Excel file
        
    Returns:
        Project: A new Project instance loaded from the Excel file
    """
    from openpyxl import load_workbook
    
    # Load the workbook
    workbook = load_workbook(filepath, data_only=True)
    
    # Read project info from the "Info" sheet
    project_info = _read_project_info_from_excel(workbook)
    
    # Read foundation loading from the "Loading" sheet
    loading = _read_foundation_loading_from_excel(workbook)
    
    # Read foundation from the "Foundation" sheet
    foundation = _read_foundation_from_excel(workbook)
    
    # Read soil from the "Soil" sheet
    soil = _read_soil_from_excel(workbook)
    
    # Read settings from the "Settings" sheet
    settings = _read_settings_from_excel(workbook)
    
    # Read design settings from the "DesignSettings" sheet
    design_settings = _read_design_settings_from_excel(workbook)
    
    
    # Create the project
    from simplex.foundation.model.project import Project
    project = Project(
        project_info=project_info,
        foundation=foundation,
        loading=loading,
        soil=soil,
        settings=settings,
        design_settings=design_settings
    )
    
    return project