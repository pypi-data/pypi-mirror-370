from dataclasses import dataclass
from simplex.core.config.environment import Environment, ENVIRONMENT

LICENSE_PREFIX = "slas/"

@dataclass(frozen=True)
class Endpoint:
    path: str
    environment: Environment = ENVIRONMENT

    @property
    def url(self) -> str:
        return f"{self.environment.base_url}{LICENSE_PREFIX}{self.path}"

class _EurocodeEndpoints:
    update_gammas = Endpoint("eurocode/EN/gamma/")

class _FoundationEndpoints:
    soil_control = Endpoint("foundation/soilCtrl/")
    rc_control = Endpoint("foundation/rcCtrl/")
    geo_design = Endpoint("foundation/geoDesign/")
    rc_design = Endpoint("foundation/rcDesign/")

class _BeamEndpoints:
     analysis = Endpoint("beam/analysis/")
     design = Endpoint("beam/design/")

class _MaterialEndpoints:
    all = Endpoint("asset/api/v1/materials/list")

    def get(self, GUID: str) -> Endpoint:
        """
        Returns the endpoint for a specific material GUID.

        Args:
            GUID (str): The GUID of the material.

        Returns:
            Endpoint: The endpoint for the material.
        """
        return Endpoint(f"asset/api/v1/materials/{GUID}")


class Endpoints:
    eurocode = _EurocodeEndpoints()
    foundation = _FoundationEndpoints()
    beam = _BeamEndpoints()
    material = _MaterialEndpoints()