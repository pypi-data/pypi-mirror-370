from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Id:
    name: str = field(default="")
    guid: str = field(default_factory=lambda: str(uuid4()))