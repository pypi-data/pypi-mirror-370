from dataclasses import dataclass, field

import simplex.core.protos.generated
import simplex.core.auth.device_flow
import simplex.core.config.endpoints
import simplex.core.config
import simplex.core.actions.fetch
import simplex.core.actions
import simplex.core.auth
import simplex.core
import simplex.core.protos
import simplex.core.protos.generated.Material
import simplex.core.protos.generated.Material.material_pb2
from simplex.foundation.model.id import Id
from abc import ABC
import simplex
import json
from google.protobuf.json_format import Parse

@dataclass
class Material(ABC):
    id: Id = field()

    _guid_map = None  # Class-level variable to store the GUID mapping

    @classmethod
    def _fetch_guid_map(cls) -> dict:
        """
        Fetches material GUIDs from the API and returns a mapping of material names to GUIDs.
        If there are duplicate names, the first occurrence is used.

        Returns:
            dict: A dictionary mapping material names to their GUIDs.
        """
        if cls._guid_map is None:  # Fetch GUIDs only once
            response = simplex.core.actions.fetch.fetch_string(
                url =  simplex.core.config.endpoints.Endpoints.material.all.url,
                token = simplex.core.auth.device_flow.get_access_token()
            ).text
            materials = json.loads(response)
            cls._guid_map = {}
            for material in materials:
                if material["name"] not in cls._guid_map:  # Only add the first occurrence
                    cls._guid_map[material["name"]] = material["guid"]
        return cls._guid_map

    @classmethod
    def _get_guid(cls, material_name: str) -> str:
        """
        Retrieves the GUID for a given material name.

        Args:
            material_name (str): The name of the material.

        Returns:
            str: The GUID of the material, or None if not found.
        """
        guid_map = cls._fetch_guid_map()
        return guid_map.get(material_name)

    def get_properties(self) -> simplex.core.protos.generated.Material.material_pb2.Data:
        fetch_string_results= simplex.core.actions.fetch.fetch_string(
                url=simplex.core.config.endpoints.Endpoints.material.get(self.id.guid).url,
                token=simplex.core.auth.device_flow.get_access_token())
        response_proto = simplex.core.protos.generated.Material.material_pb2.Data()
        Parse(fetch_string_results.text, response_proto)
        return response_proto

@dataclass
class Concrete(Material):

    @classmethod
    def C12_15(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C12/15 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C12/15" and a specific GUID.
        """
        guid = cls._get_guid("C12/15")
        return cls(id=Id(name="C12/15", guid=guid))

    @classmethod
    def C16_20(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C16/20 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C16/20" and a specific GUID.
        """
        guid = cls._get_guid("C16/20")
        return cls(id=Id(name="C16/20", guid=guid))

    @classmethod
    def C20_25(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C20/25 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C20/25" and a specific GUID.
        """
        guid = cls._get_guid("C20/25")
        return cls(id=Id(name="C20/25", guid=guid))

    @classmethod
    def C25_30(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C25/30 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C25/30" and a specific GUID.
        """
        guid = cls._get_guid("C25/30")
        return cls(id=Id(name="C25/30", guid=guid))

    @classmethod
    def C28_35(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C28/35 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C28/35" and a specific GUID.
        """
        guid = cls._get_guid("C28/35")
        return cls(id=Id(name="C28/35", guid=guid))
    
    @classmethod
    def C30_37(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C30/37 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C30/37" and a specific GUID.
        """
        guid = cls._get_guid("C30/37")
        return cls(id=Id(name="C30/37", guid=guid))

    @classmethod
    def C32_40(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C32/40 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C32/40" and a specific GUID.
        """
        guid = cls._get_guid("C32/40")
        return cls(id=Id(name="C32/40", guid=guid))

    @classmethod
    def C35_45(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C35/45 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C35/45" and a specific GUID.
        """
        guid = cls._get_guid("C35/45")
        return cls(id=Id(name="C35/45", guid=guid))

    @classmethod
    def C40_50(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C40/50 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C40/50" and a specific GUID.
        """
        guid = cls._get_guid("C40/50")
        return cls(id=Id(name="C40/50", guid=guid))

    @classmethod
    def C45_55(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C45/55 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C45/55" and a specific GUID.
        """
        guid = cls._get_guid("C45/55")
        return cls(id=Id(name="C45/55", guid=guid))

    @classmethod
    def C50_60(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C50/60 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C50/60" and a specific GUID.
        """
        guid = cls._get_guid("C50/60")
        return cls(id=Id(name="C50/60", guid=guid))

    @classmethod
    def C54_65(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C54/65 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C54/65" and a specific GUID.
        """
        guid = cls._get_guid("C54/65")
        return cls(id=Id(name="C54/65", guid=guid))

    @classmethod
    def C55_67(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C55/67 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C55/67" and a specific GUID.
        """
        guid = cls._get_guid("C55/67")
        return cls(id=Id(name="C55/67", guid=guid))

    @classmethod
    def C58_70(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C58/70 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C58/70" and a specific GUID.
        """
        guid = cls._get_guid("C58/70")
        return cls(id=Id(name="C58/70", guid=guid))

    @classmethod
    def C60_75(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C60/75 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C60/75" and a specific GUID.
        """
        guid = cls._get_guid("C60/75")
        return cls(id=Id(name="C60/75", guid=guid))

    @classmethod
    def C70_85(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C70/85 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C70/85" and a specific GUID.
        """
        guid = cls._get_guid("C70/85")
        return cls(id=Id(name="C70/85", guid=guid))

    @classmethod
    def C80_95(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C80/95 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C80/95" and a specific GUID.
        """
        guid = cls._get_guid("C80/95")
        return cls(id=Id(name="C80/95", guid=guid))

    @classmethod
    def C90_105(cls) -> "Concrete":
        """
        Creates and returns a Concrete instance representing the C90/105 concrete grade.

        Returns:
            Concrete: An instance of the Concrete class with the ID set to "C90/105" and a specific GUID.
        """
        guid = cls._get_guid("C90/105")
        return cls(id=Id(name="C90/105", guid=guid))
    
    @classmethod
    def get_curr_co2_index(cls, mat_name) -> float:
        kg_m3 = 2350

        co2_factors = {
            "C12/15": 0,
            "C16/20": 0,
            "C20/25": 0.122,
            "C25/30": 0.129,
            "C28/35": 0.136,
            "C30/37": 0.145,
            "C32/40": 0.148,
            "C35/45": 0.163,
            "C40/50": 0.175,
            "C45/55": 0.189,
            "C50/60": 0.204,
            "C54/65": 0,
            "C55/67": 0.220,
            "C58/70": 0,
            "C60/75": 0.230,
            "C70/85": 0,
            "C80/95": 0,
            "C90/105": 0,
        }

        factor = co2_factors.get(mat_name, 0)
        return factor * kg_m3



@dataclass
class Reinforcement(Material):
    @classmethod
    def B500(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B500 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B500" and a specific GUID.
        """
        guid = cls._get_guid("B500")
        return cls(id=Id(name="B500", guid=guid))


    @classmethod
    def N(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the N reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "N" and a specific GUID.
        """
        guid = cls._get_guid("N")
        return cls(id=Id(name="N", guid=guid))


    @classmethod
    def K(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the K reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "K" and a specific GUID.
        """
        guid = cls._get_guid("K")
        return cls(id=Id(name="K", guid=guid))


    @classmethod
    def Y(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the Y reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "Y" and a specific GUID.
        """
        guid = cls._get_guid("Y")
        return cls(id=Id(name="Y", guid=guid))


    @classmethod
    def Z(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the Z reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "Z" and a specific GUID.
        """
        guid = cls._get_guid("Z")
        return cls(id=Id(name="Z", guid=guid))


    @classmethod
    def R(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the R reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "R" and a specific GUID.
        """
        guid = cls._get_guid("R")
        return cls(id=Id(name="R", guid=guid))


    @classmethod
    def Ss260(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the Ss260 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "Ss260" and a specific GUID.
        """
        guid = cls._get_guid("Ss260")
        return cls(id=Id(name="Ss260", guid=guid))


    @classmethod
    def B500B(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B500B reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B500B" and a specific GUID.
        """
        guid = cls._get_guid("B500B")
        return cls(id=Id(name="B500B", guid=guid))

    @classmethod
    def Ks600(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the Ks600 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "Ks600" and a specific GUID.
        """
        guid = cls._get_guid("Ks600")
        return cls(id=Id(name="Ks600", guid=guid))

    @classmethod
    def Ps500(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the Ps500 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "Ps500" and a specific GUID.
        """
        guid = cls._get_guid("Ps500")
        return cls(id=Id(name="Ps500", guid=guid))

    @classmethod
    def G250(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the G250 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "G250" and a specific GUID.
        """
        return cls(id=Id(name="G250", guid="d108deb4-5dde-4cd7-a1d1-bd43b3630527"))

    @classmethod
    def B500A(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B500A reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B500A" and a specific GUID.
        """
        guid = cls._get_guid("B500A")
        return cls(id=Id(name="B500A", guid=guid))

    @classmethod
    def B500B(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B500B reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B500B" and a specific GUID.
        """
        guid = cls._get_guid("B500B")
        return cls(id=Id(name="B500B", guid=guid))

    @classmethod
    def B500C(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B500C reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B500C" and a specific GUID.
        """
        guid = cls._get_guid("B500C")
        return cls(id=Id(name="B500C", guid=guid))

    @classmethod
    def S235JRG2(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the S235JRG2 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "S235JRG2" and a specific GUID.
        """
        return cls(id=Id(name="S235JRG2", guid="b6df5a5b-a759-4d08-a699-e125b34545f8"))

    @classmethod
    def A500HW(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the A500HW reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "A500HW" and a specific GUID.
        """
        guid = cls._get_guid("A500HW")
        return cls(id=Id(name="A500HW", guid=guid))

    @classmethod
    def A700HW(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the A700HW reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "A700HW" and a specific GUID.
        """
        guid = cls._get_guid("A700HW")
        return cls(id=Id(name="A700HW", guid=guid))

    @classmethod
    def B500K(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B500K reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B500K" and a specific GUID.
        """
        guid = cls._get_guid("B500K")
        return cls(id=Id(name="B500K", guid=guid))

    @classmethod
    def B600KX(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B600KX reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B600KX" and a specific GUID.
        """
        guid = cls._get_guid("B600KX")
        return cls(id=Id(name="B600KX", guid=guid))

    @classmethod
    def B700K(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the B700K reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "B700K" and a specific GUID.
        """ 
        guid = cls._get_guid("B700K")
        return cls(id=Id(name="B700K", guid=guid))

    @classmethod
    def _250(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the 250 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "250" and a specific GUID.
        """
        guid = cls._get_guid("250")
        return cls(id=Id(name="250", guid=guid))


    @classmethod
    def _420(cls) -> "Reinforcement":
        """
        Creates and returns a Reinforcement instance representing the 420 reinforcement grade.

        Returns:
            Reinforcement: An instance of the Reinforcement class with the ID set to "420" and a specific GUID.
        """
        guid = cls._get_guid("420")
        return cls(id=Id(name="420", guid=guid))
