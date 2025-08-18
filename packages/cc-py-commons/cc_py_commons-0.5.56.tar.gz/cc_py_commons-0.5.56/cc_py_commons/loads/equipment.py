import uuid
from dataclasses import dataclass, field

@dataclass
class Equipment:

    id: uuid.UUID
    name: str
    active: bool = field(default=True)
