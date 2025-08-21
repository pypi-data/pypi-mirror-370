import simplex.core.materials
import simplex.core.auth.device_flow
import simplex.core.auth
import simplex.core.config.endpoints
import simplex.core.config
import simplex.core.actions.fetch
import simplex.core.actions
import simplex.foundation.model.project
import simplex.core.protos.generated.Design
import simplex.core.protos.generated.Design.concrete_pb2
import simplex.core.protos.generated.Geometry.reinf_pb2
import simplex.foundation.model.reinforcement
import simplex.core.numbers.units
import simplex.core.numbers
import simplex.core.protos.generated.Material
import simplex.core.protos.generated.Material.material_pb2
import simplex.core.protos.generated.Material.soil_pb2
import simplex.core.protos.generated.Soilmodel
import simplex.core.protos.generated.Soilmodel.soil_model_pb2
import simplex.foundation.model.soil
import simplex.core.protos.generated.Frontends
import simplex.core.protos.generated.Frontends.foundation_pb2
import simplex.core.protos.generated.Geometry
import simplex.core.protos.generated.Geometry.geometry_pb2
import simplex.core.protos.generated.Loading
import simplex.core.protos.generated.Loading.load_pb2
import simplex.core.protos.generated.Loading.loadcase_pb2
import simplex.core.protos.generated.Loading.loadcombination_pb2
import simplex.foundation
import simplex.foundation.model
import simplex.foundation.model.foundation
import simplex.foundation.model.foundation_loading
from simplex.foundation.model.project import Project, ProjectInfo
from simplex.core.protos.generated.Frontends import foundation_pb2
import simplex.core.protos.generated.project_pb2
import simplex
from google.protobuf.json_format import Parse
import os
from uuid import uuid4
from datetime import datetime
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
from typing import List
from simplex.core.protos.generated.Design import concrete_pb2
import importlib.resources


import simplex.foundation.model.settings

def convert_to_frontend_project_proto(project: Project) -> foundation_pb2.Project:
    proto = _load_template_json()
    _set_meta(project, proto)
    _set_data(project, proto)
    _set_design_settings(project, proto)
    return proto

# --- Step 1: Load Template
def _load_template_json() -> foundation_pb2.Project:
    with importlib.resources.files("simplex.foundation").joinpath("default_project.json").open("r") as f:
        return Parse(f.read(), foundation_pb2.Project())

# --- Step 2: Set Metadata
def _set_meta(project: Project, proto: simplex.core.protos.generated.Frontends.foundation_pb2.Project):
    _set_project_info(project.project_info, proto)

# --- Step 3: Set .data content
def _set_data(project: Project, proto: simplex.core.protos.generated.Frontends.foundation_pb2.Project):
    data = proto.data
    _set_project_settings(project.settings, data)
    _set_foundation(project.foundation, data)
    _add_foundation_loading(project.loading, data)
    _set_soil_model(project.soil, data)

def _get_cover_and_spaces(project : simplex.foundation.model.project.Project) -> List[concrete_pb2.CoverAndSpace]:
    distances: List[concrete_pb2.CoverAndSpace] = []

    reinforcement = project.foundation.reinforcement
    if reinforcement is None:
        dist = concrete_pb2.CoverAndSpace(
            cover=50,
            space=50,
            side=concrete_pb2.BEAM_SIDE_UNSPECIFIED,
        )
        distances.append(dist)
    else:
        layers = reinforcement.layers

        top_covers = [layer.concrete_cover for layer in layers if layer.zone == simplex.foundation.model.reinforcement.Zone.TOP]
        bottom_covers = [layer.concrete_cover for layer in layers if layer.zone == simplex.foundation.model.reinforcement.Zone.BOTTOM]
        top_cover = min(top_covers) if top_covers else 50
        bottom_cover = min(bottom_covers) if bottom_covers else 50
        side_cover = layers[0].side_cover if layers[0].side_cover else 50

        for side_zone in simplex.foundation.model.reinforcement.Zone:
            cover = 50
            space = 100
            vgap = 20

            if side_zone == simplex.foundation.model.reinforcement.Zone.TOP:
                cover = top_cover
                space = vgap
            elif side_zone == simplex.foundation.model.reinforcement.Zone.BOTTOM:
                cover = bottom_cover
                space = vgap
            else:
                cover = side_cover
                space = vgap

            dist = concrete_pb2.CoverAndSpace(
                cover=cover,
                space=space,
                side=side_zone.value,
            )
            distances.append(dist)


    return distances

def _set_design_settings(project: Project, proto: simplex.core.protos.generated.Frontends.foundation_pb2.Project):
    if project.design_settings is None:
        return
    proto_design = convert_to_auto_design_proto(project.design_settings)
    proto_design.settings[0].element_guid = project.foundation.id.guid

    proto_design.settings[0].concrete.btm_dia_mtrl_guid = (
        simplex.core.materials.Reinforcement.B500B().id.guid
        if project.foundation.reinforcement is None
        else project.foundation.reinforcement.material.id.guid
    )

    # set distances
    ng_cover_and_spaces = _get_cover_and_spaces(project)
    proto_design.settings[0].concrete.distances.extend(ng_cover_and_spaces)
    proto.settings.endpoint_cache.auto_design.CopyFrom(proto_design)


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
    auto_design.active = design_settings._active
    auto_design.settings.append(settings)

    return auto_design


def _set_project_info(project_info: ProjectInfo, proto : simplex.core.protos.generated.Frontends.foundation_pb2.Project):
    meta = proto.meta
    meta.project = project_info.project or ""
    meta.name = project_info.name or ""
    meta.description = project_info.description or ""
    meta.location = project_info.location or ""
    meta.company = project_info.company or ""
    meta.signature = project_info.signature or ""
    meta.comments = project_info.comments or ""
    meta.last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Data Subsections
def _set_foundation(fnd: simplex.foundation.model.foundation.FoundationBase, data : simplex.core.protos.generated.project_pb2):
    _set_foundation_geometry(fnd, data)
    _set_foundation_reinforcement(fnd, data)
    _add_element_stage(fnd, data)
    pass

def _add_element_stage(fnd: simplex.foundation.model.foundation.FoundationBase, data : simplex.core.protos.generated.project_pb2):
    data.input.structures[0].stages[0].elems[0].guid = f"{fnd.id.guid}"
    data.input.structures[0].stages[0].elems[0].rc.rc_specifics[0].guid = "" ### TO BE FIXED it needs a method that look in a database

def _set_foundation_geometry(fnd: simplex.foundation.model.foundation.FoundationBase, data : simplex.core.protos.generated.project_pb2):
    data.input.structures[0].elements[0].id.guid = f"{fnd.id.guid}"
    data.input.structures[0].elements[0].id.name = f"{fnd.id.name}"

    data.input.structures[0].elements[0].foundation.simple_foundation.geometry.height = fnd.height

    data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.x = fnd.position.x
    data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.y = fnd.position.y
    data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.z =  - fnd.height + fnd.top_of_footing

    if(isinstance(fnd, simplex.foundation.model.foundation.RectangularFoundation)):
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.width = fnd.lx_bottom
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.width_top = fnd.lx_top
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.length = fnd.ly_bottom
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.length_top = fnd.ly_top
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.eccentricity_width_top = fnd.eccentricity_x
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.eccentricity_length_top = fnd.eccentricity_y
    elif(isinstance(fnd, simplex.foundation.model.foundation.LineFoundation)):
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.line_foundation.width = fnd.lx_bottom
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.line_foundation.width_top = fnd.lx_top
        data.input.structures[0].elements[0].foundation.simple_foundation.geometry.line_foundation.eccentricity_width_top = fnd.eccentricity_x

    # material
    _add_material(fnd.material, data)
    data.input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.mtrl_guid = fnd.material.id.guid

def _set_foundation_reinforcement(fnd: simplex.foundation.model.foundation.FoundationBase, data : simplex.core.protos.generated.project_pb2):
    if fnd.reinforcement is None:
        return

    def _add_reinforcement_layers(layers : list[simplex.foundation.model.reinforcement.ReinfLayer], length : float, direction_vector):
        for layer in layers:
            group_id = f"{uuid4()}"

            ng_grps = simplex.core.protos.generated.Geometry.reinf_pb2.Group()
            ng_grps.start = 0
            ng_grps.length = length
            ng_grps.mtrl_guid = layer.material.id.guid
            ng_grps.diameter = layer.diameter
            ng_grps.id.guid = group_id
            ng_grps.id.name = ""
            ng_grps.direction.x = direction_vector.x
            ng_grps.direction.y = direction_vector.y
            ng_grps.direction.z = direction_vector.z

            data.input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.rebars.grps.append(ng_grps)

            ng_layer = simplex.core.protos.generated.Geometry.reinf_pb2.Layer()
            ng_layer.level = 1
            ng_layer.zone = layer.zone.value
            ng_layer.min_free_space = 30
            ng_layer.d = int(layer.concrete_cover)
            ng_layer.id.guid = f"{uuid4()}"
            ng_layer.id.name = ""
            ng_layer.s = int(layer.spacing)
            ng_layer.grp_guid = group_id

            data.input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.rebars.lays.append(ng_layer)

    if isinstance(fnd, simplex.foundation.model.foundation.RectangularFoundation):
        _add_reinforcement_layers(
            fnd.reinforcement.x_direction,
            fnd.lx_bottom,
            simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=1, y=0, z=0)
        )
        _add_reinforcement_layers(
            fnd.reinforcement.y_direction,
            fnd.ly_bottom,
            simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=0, y=1, z=0)
        )

    if isinstance(fnd, simplex.foundation.model.foundation.LineFoundation):
        _add_reinforcement_layers(
            fnd.reinforcement.x_direction,
            fnd.lx_bottom,
            simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=1, y=0, z=0)
        )

    _add_material(fnd.reinforcement.material, data)


def _add_foundation_loading(loading: list[simplex.foundation.model.foundation_loading.FoundationLoading], data : simplex.core.protos.generated.project_pb2):
    
    _add_gravity_load_case(data)

    for fnd_loading in loading:
        _add_load_case(fnd_loading, data)
        _add_load(fnd_loading, data)
        _add_load_combination(fnd_loading, data)
        _add_combination_stage(fnd_loading, data)

def _add_gravity_load_case(data : simplex.core.protos.generated.project_pb2):

    ng_load_case = simplex.core.protos.generated.Loading.loadcase_pb2.Data()
    ng_load_case.id.name = f"SW"
    ng_load_case.id.guid = str(uuid4())
    ng_load_case.type = simplex.core.protos.generated.Loading.loadcase_pb2.TYPE_SELF_WEIGHT
    ng_load_case.duration_class = simplex.core.protos.generated.Loading.loadcase_pb2.DURATION_CLASS_PERMANENT
    ng_load_case.category = simplex.core.protos.generated.Loading.loadcase_pb2.CATEGORY_UNSPECIFIED
    ng_load_case.number_of_storeys = 1

    data.input.structures[0].loading.loadcases.append(ng_load_case)
    return

def _add_load_case(fnd_loading: simplex.foundation.model.foundation_loading.FoundationLoading, data : simplex.core.protos.generated.project_pb2):

    ng_load_case = simplex.core.protos.generated.Loading.loadcase_pb2.Data()
    ng_load_case.id.name = f"Loadcase for {fnd_loading.id.name}"
    ng_load_case.id.guid = str(fnd_loading._load_case_id)
    ng_load_case.type = simplex.core.protos.generated.Loading.loadcase_pb2.TYPE_PERMANENT_LOAD
    ng_load_case.category = simplex.core.protos.generated.Loading.loadcase_pb2.CATEGORY_A
    ng_load_case.duration_class = simplex.core.protos.generated.Loading.loadcase_pb2.DURATION_CLASS_PERMANENT
    ng_load_case.number_of_storeys = 1

    data.input.structures[0].loading.loadcases.append(ng_load_case)
    return 

def _add_load_combination(fnd_loading: simplex.foundation.model.foundation_loading.FoundationLoading, data : simplex.core.protos.generated.project_pb2):

    ng_load_combination = simplex.core.protos.generated.Loading.loadcombination_pb2.Data()
    ng_load_combination.type = fnd_loading.type.value
    ng_load_combination.limit_state = simplex.core.protos.generated.Loading.loadcombination_pb2.LIMIT_STATE_STR

    part = simplex.core.protos.generated.Loading.loadcombination_pb2.CombinationPart()
    part.lcase_guid = str(fnd_loading._load_case_id)
    coefficient = simplex.core.protos.generated.Loading.loadcombination_pb2.Coefficient(type = simplex.core.protos.generated.Loading.loadcombination_pb2.COEFFICIENT_TYPE_BASE, value= 1)
    part.coefficients.append( coefficient )
    ng_load_combination.parts.append(part)
    
    if(fnd_loading.sw != 0):
        part = simplex.core.protos.generated.Loading.loadcombination_pb2.CombinationPart()
        sw_guid = next( (x.id.guid for x in data.input.structures[0].loading.loadcases if x.id.name == "SW") )
        part.lcase_guid = sw_guid
        coefficient = simplex.core.protos.generated.Loading.loadcombination_pb2.Coefficient(type = simplex.core.protos.generated.Loading.loadcombination_pb2.COEFFICIENT_TYPE_GAMMA, value= fnd_loading.sw)
        part.coefficients.append( coefficient )
        ng_load_combination.parts.append(part)
    
    ng_load_combination.geo_type = simplex.core.protos.generated.Loading.loadcombination_pb2.GEO_TYPE_2
    ng_load_combination.coa = simplex.core.protos.generated.Loading.loadcombination_pb2.COA_TYPE_610A
    ng_load_combination.id.guid = f"{fnd_loading._load_combination_id}"
    ng_load_combination.id.name = f"{fnd_loading.id.name}"
    ng_load_combination.foundation_config.ground_water_guid = f"{data.input.soil_model.ground_waters[0].id.guid}"

    data.input.structures[0].loading.combinations.append(ng_load_combination)
    pass

def _add_combination_stage(fnd_loading: simplex.foundation.model.foundation_loading.FoundationLoading, data : simplex.core.protos.generated.project_pb2):
    data.input.structures[0].stages[0].lcomb_guids.append(f"{fnd_loading._load_combination_id}")

def _add_load(fnd_loading: simplex.foundation.model.foundation_loading.FoundationLoading, data : simplex.core.protos.generated.project_pb2):
    components = [
        ("hx",  fnd_loading.hx * 1000, simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=1,y=0,z=0), simplex.core.protos.generated.Loading.load_pb2.TYPE_FORCE),
        ("hy",  fnd_loading.hy * 1000, simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=0,y=1,z=0), simplex.core.protos.generated.Loading.load_pb2.TYPE_FORCE),
        ("n",  fnd_loading.n * 1000,  simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=0,y=0,z=1), simplex.core.protos.generated.Loading.load_pb2.TYPE_FORCE),
        ("mx", getattr(fnd_loading, "mx", 0) * 1000, simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=1,y=0,z=0), simplex.core.protos.generated.Loading.load_pb2.TYPE_MOMENT),
        ("my", fnd_loading.my * 1000, simplex.core.protos.generated.Geometry.geometry_pb2.Vector3D(x=0,y=1,z=0), simplex.core.protos.generated.Loading.load_pb2.TYPE_MOMENT)
    ]

    for suffix, value, direction, load_type in components:
        load_data = simplex.core.protos.generated.Loading.load_pb2.Data()

        # Unique ID
        load_data.id.guid = f"{fnd_loading.name}_{suffix}"
        load_data.id.name = f"{fnd_loading.name}_{suffix}"

        # Core properties
        load_data.type = load_type
        load_data.distribution = simplex.core.protos.generated.Loading.load_pb2.DISTRIBUTION_TYPE_POINT
        load_data.lcase_guid = str(fnd_loading._load_case_id)
        load_data.assigned_objects.append( str( data.input.structures[0].elements[0].id.guid ))

        # Direction
        load_data.direction.x = direction.x
        load_data.direction.y = direction.y
        load_data.direction.z = direction.z
        # Position — assuming single point at origin (can customize)
        if( isinstance(fnd_loading, simplex.foundation.model.foundation_loading.PointFoundationLoading)):
            x = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.x + data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.eccentricity_width_top
            y = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.y + data.input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle.eccentricity_length_top
            z = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.z + data.input.structures[0].elements[0].foundation.simple_foundation.geometry.height
        elif( isinstance(fnd_loading, simplex.foundation.model.foundation_loading.LineFoundationLoading)):
            x = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.x + data.input.structures[0].elements[0].foundation.simple_foundation.geometry.line_foundation.eccentricity_width_top
            y = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.y
            z = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.z + data.input.structures[0].elements[0].foundation.simple_foundation.geometry.height

        pos = simplex.core.protos.generated.Geometry.geometry_pb2.Point3D(x=x, y=y, z=z)
        load_data.positions.append(pos)
        # Value
        load_data.values.append(value)

        # Add all loads to the data
        data.input.structures[0].loading.loads.append(load_data)
        pass

def _set_soil_model(soil: simplex.foundation.model.soil.SoilBase, data : simplex.core.protos.generated.project_pb2):
    _set_soil(soil, data)

    if isinstance(soil, simplex.foundation.model.soil.SoilComplex):
        _set_ground_water(soil, data)
        _set_soil_stratum(soil, data)
        _set_bore_hole(soil, data)
        _add_soil_materials(soil, data)
    pass

def _set_ground_water(soil: simplex.foundation.model.soil.SoilBase, data : simplex.core.protos.generated.project_pb2):
    ground_water_guids = f"{soil._ground_water_level_guid}"
    data.input.soil_model.ground_waters[0].id.guid = ground_water_guids
    data.input.soil_model.ground_waters[0].id.name = "Ground water"

    for combo in data.input.structures[0].loading.combinations:
        combo.foundation_config.ground_water_guid = ground_water_guids

def _set_bore_hole(soil_complex: simplex.foundation.model.soil.SoilComplex, data : simplex.core.protos.generated.project_pb2):
    data.input.soil_model.bore_holes[0].id.guid = soil_complex.borehole.id.guid
    data.input.soil_model.bore_holes[0].id.name = soil_complex.borehole.id.name

    del data.input.soil_model.bore_holes[0].ground_water_levels[:]
    data.input.soil_model.bore_holes[0].ground_water_levels.append(soil_complex.ground_water)
 
    del data.input.soil_model.bore_holes[0].soil_stratum_top_levels[:] # Clear existing levels to avoid duplicates
    data.input.soil_model.bore_holes[0].soil_stratum_top_levels.extend(soil_complex.borehole.top_of_layers)
    data.input.soil_model.bore_holes[0].final_ground_level = soil_complex.borehole.top_of_layers[0]

    data.input.soil_model.bore_holes[0].soil_guid = soil_complex.id.guid

    data.input.soil_model.bore_holes[0].placement.x = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.x
    data.input.soil_model.bore_holes[0].placement.y = data.input.structures[0].elements[0].foundation.simple_foundation.geometry.center.y

    data.input.structures[0].elements[0].foundation.simple_foundation.borehole_guid =  soil_complex.borehole.id.guid

    pass
    
def _set_soil(soil: simplex.foundation.model.soil.SoilBase, data : simplex.core.protos.generated.project_pb2):
    data.input.soil_model.soils[0].id.guid = soil.id.guid
    data.input.soil_model.soils[0].id.name = soil.id.name
    data.input.soil_model.bore_holes[0].soil_guid = soil.id.guid

    if isinstance(soil, simplex.foundation.model.soil.SoilComplex):

        del data.input.soil_model.soils[0].soil_stratum_guids[:]

        data.input.soil_model.soils[0].perform_soil_calculations = True
        data.input.soil_model.soils[0].limit_depth = soil.depth_limit
        data.input.soil_model.soils[0].ground_water_guids[0] = f"{soil._ground_water_level_guid}"
        data.input.soil_model.soils[0].soil_stratum_guids.extend( f"{guid}" for guid in soil._stratum_guids )
    elif isinstance(soil, simplex.foundation.model.soil.SoilSimple):
        data.input.soil_model.soils[0].perform_soil_calculations = False
        data.input.soil_model.soils[0].allowed_soil_pressure.allowed_soil_pressure_sls = soil.allowed_soil_pressure_sls * 1000
        data.input.soil_model.soils[0].allowed_soil_pressure.allowed_soil_pressure_uls = soil.allowed_soil_pressure_uls * 1000
        data.input.soil_model.soils[0].allowed_soil_pressure.friction_coef = soil.friction_coefficient
    else:
        raise TypeError("Unsupported soil type")
    pass

def _set_soil_stratum(soil: simplex.foundation.model.soil.SoilComplex, data : simplex.core.protos.generated.project_pb2):
    del data.input.soil_model.soil_stratums[:]

    for i, soil_material in enumerate(soil.borehole.soil_materials):
        soil_stratum = simplex.core.protos.generated.Soilmodel.soil_model_pb2.SoilStratum()
        soil_stratum.soil_material_guid = soil_material.id.guid
        soil_stratum.id.guid = f"{soil._stratum_guids[i]}"
        soil_stratum.id.name = f"stratum_{i}"

        data.input.soil_model.soil_stratums.append(soil_stratum)
    pass
    
def _set_project_settings(settings: simplex.foundation.model.settings.Settings, data : simplex.core.protos.generated.project_pb2):
    _set_code_settings(settings.code, data)
    _set_concrete_settings(settings.concrete_sett, data)
    _set_soil_settings(settings.soil_sett, data)

def _set_code_settings(settings: simplex.foundation.model.settings.CodeSettings, data : simplex.core.protos.generated.project_pb2):
    data.input.ec.national_annex = settings.annex.value
    data.input.structures[0].cc = settings.consequence.value
    data.input.structures[0].reliability_class = settings.reliability.value

def _set_concrete_settings(settings: simplex.foundation.model.settings.ConcreteSettings, data : simplex.core.protos.generated.project_pb2):
    data.input.structures[0].design_settings.rc.crk_conv =  settings.crack
    data.input.structures[0].design_settings.rc.crack_check = True

    data.input.structures[0].elements[0].design_settings.soil.foundation_element_configuration.foundation_distribution = settings.distribution.value

    data.input.structures[0].elements[0].design_settings.rc.fabrication = settings.fabrication.value
    data.input.structures[0].elements[0].design_settings.rc.low_strength_variation = settings.low_strength_variation
    data.input.structures[0].elements[0].design_settings.rc.beam.use_min_reinf = settings.consider_min_reinforcement

    data.input.structures[0].elements[0].inspection_level = settings.inspection_level.value
    data.input.structures[0].elements[0].critical = settings.critical_element

    data.input.structures[0].stages[0].elems[0].rc.rc_specifics[0].exposure_class = settings.exposure_class.value
    data.input.structures[0].stages[0].elems[0].rc.life_category = settings.life_category.value

def _set_soil_settings(settings: simplex.foundation.model.settings.SoilSettings, data : simplex.core.protos.generated.project_pb2):
    data.input.structures[0].design_settings.soil.foundation_configuration.design_approach = settings.des_appr.value
    data.input.structures[0].design_settings.soil.geotechnical_category = settings.geo_cat.value
    data.input.structures[0].elements[0].design_settings.soil.foundation_element_configuration.settlement_configuration.check_absolute_settlement = settings.check_settl
    data.input.structures[0].elements[0].design_settings.soil.foundation_element_configuration.settlement_configuration.absolute_settlement = settings.abs_sttl / 1000
    data.input.structures[0].elements[0].design_settings.soil.foundation_element_configuration.soil_punching_type = settings.punching.value


def _add_material(material: simplex.core.materials.Material, data : simplex.core.protos.generated.project_pb2):
    
    def fetch_material(material) -> simplex.core.protos.generated.Material.material_pb2.Data:
        fetch_string_results= simplex.core.actions.fetch.fetch_string(
                url=simplex.core.config.endpoints.Endpoints.material.get(material.id.guid).url,
                token=simplex.core.auth.device_flow.get_access_token())
        response_proto = simplex.core.protos.generated.Material.material_pb2.Data()
        Parse(fetch_string_results.text, response_proto)
        return response_proto

    ng_concrete_material = fetch_material(material)

    # Check if material already exists in mtrl_db by guid
    if not any(m.id.guid == ng_concrete_material.id.guid for m in data.input.mtrl_db):
        data.input.mtrl_db.append(ng_concrete_material)


def _add_soil_materials(soil_material: simplex.foundation.model.soil.SoilComplex, data : simplex.core.protos.generated.project_pb2):
    soil_materials = soil_material.borehole.soil_materials
    for soil_material in soil_materials:
        ng_soil_material = simplex.core.protos.generated.Material.material_pb2.Data()
        ng_soil_material.id.guid = soil_material.id.guid
        ng_soil_material.id.name = soil_material.id.name
        ng_soil_material.type = simplex.core.protos.generated.Material.material_pb2.MTRL_SOIL

        ng_soil_material.soil_data.id.guid = soil_material.id.guid
        ng_soil_material.soil_data.id.name = soil_material.id.name
        ng_soil_material.soil_data.behaviour = soil_material.drainage.value
        ng_soil_material.soil_data.material_model = soil_material.material_model.value
        ng_soil_material.soil_data.properties.gamma = soil_material.gamma * 1000                # Convert to kN/m^3
        ng_soil_material.soil_data.properties.gamma_effective = soil_material.gamma_eff * 1000  # Convert to kN/m^3
        ng_soil_material.soil_data.properties.m0 = soil_material.m0 * 1000                      # Convert to kN/m^3
        ng_soil_material.soil_data.properties.phi_k = soil_material.phik
        ng_soil_material.soil_data.properties.ck = soil_material.ck * 1000                      # Convert to kN/m^2
        ng_soil_material.soil_data.properties.cuk = soil_material.cuk * 1000                    # Convert to kN/m^2
        ng_soil_material.soil_data.properties.rk = soil_material.rk * 1000                      # Convert to kN/m^2


        if not any(m.id.guid == ng_soil_material.id.guid for m in data.input.mtrl_db):
            data.input.mtrl_db.append(ng_soil_material)