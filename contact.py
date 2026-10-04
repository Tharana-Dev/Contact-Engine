import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Contact:
    first_name: str
    last_name: str
    phone: str
    email: str
    id: int | None = None

    def __post_init__(self) -> None:
        if not (self.first_name.strip() and self.last_name.strip() and self.phone.strip() and self.email.strip()):
            raise ValueError("No fields can be left blank")

        object.__setattr__(self, "first_name", self.first_name.strip())
        object.__setattr__(self, "last_name", self.last_name.strip())
        object.__setattr__(self, "phone", self.phone.strip())
        object.__setattr__(self, "email", self.email.strip())