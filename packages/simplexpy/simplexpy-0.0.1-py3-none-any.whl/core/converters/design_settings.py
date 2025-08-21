import simplex.core.protos.generated
import simplex.core
import simplex.core.protos
import simplex.core.protos.generated.EndPointArguments
import simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2
import simplex.core.protos.generated.Frontends
import simplex.core.protos.generated.Frontends.foundation_pb2
from simplex.foundation.design.auto_design import DesignSettings
from simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2 import AutoDesign, AutoDesignSettings
import simplex

def convert_to_auto_design_proto(design_settings: DesignSettings) -> simplex.core.protos.generated.EndPointArguments.common_api_functions_pb2.AutoDesign:

    settings = AutoDesignSettings()
    settings.limit_utilization = design_settings.limit_utilisation

    # Foundation settings
    if design_settings.foundation_settings is not None:
        settings.foundation.length_width_ratio = design_settings.foundation_settings.length_width_ratio

        settings.foundation.width.min = design_settings.foundation_settings.width.min
        settings.foundation.width.max = design_settings.foundation_settings.width.max
        settings.foundation.width.step = design_settings.foundation_settings.width.step

        settings.foundation.length.min = design_settings.foundation_settings.length.min
        settings.foundation.length.max = design_settings.foundation_settings.length.max
        settings.foundation.length.step = design_settings.foundation_settings.length.step

        settings.foundation.height.min = design_settings.foundation_settings.height.min
        settings.foundation.height.max = design_settings.foundation_settings.height.max
        settings.foundation.height.step = design_settings.foundation_settings.height.step

    #concrete settings
    if design_settings.concrete_settings is not None:
        settings.concrete.spacing_limits.min = design_settings.concrete_settings.spacing_limits.min
        settings.concrete.spacing_limits.max = design_settings.concrete_settings.spacing_limits.max
        settings.concrete.spacing_limits.step = design_settings.concrete_settings.spacing_limits.step

        # method for set distances
        settings.concrete.btm_dia.extend(design_settings.concrete_settings.rnfr_dia)


    auto_design = AutoDesign()
    auto_design.active = True
    auto_design.settings.append(settings)

    return auto_design