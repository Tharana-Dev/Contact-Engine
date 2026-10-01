import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class Contact:
    first_name: str
    last_name: str
    phone: str
    email: str 

    def __post_init__(self) -> None:
        if not (self.first_name.strip() and self.last_name.strip() and self.phone.strip() and self.email.strip()):
            raise ValueError("No fields can be left blank")
        
        object.__setattr__(self, "first_name", self.first_name.strip())
        object.__setattr__(self, "last_name", self.last_name.strip())
        object.__setattr__(self, "phone", self.phone.strip())
        object.__setattr__(self, "email", self.email.strip())

class ContactBook:
    def __init__(self, contacts: list[Contact] | None = None) -> None:
        self.contacts: list[Contact] = list(contacts) if contacts else []


    def add(self, f_name:str, l_name:str, phone:str, email:str) -> Contact:
        """Create a Contact and append it. Returns the new contact."""
        contact = Contact(
            first_name=f_name,
            last_name=l_name,
            phone=phone,
            email=email
            )
        self.contacts.append(contact)
        return contact

    def remove(self, index: int) -> Contact:
        """Remove and return the contact at `index` (negative indices allowed)."""
        try:
            return self.contacts.pop(index)
        except IndexError:
            raise IndexError(
                f"no contact at index {index} (book has {len(self.contacts)} entries)"
            ) from None

    def save(self, path: str | Path) -> None:
        """Write the whole book to `path` as JSON."""
        path = Path(path)
        payload = [asdict(c) for c in self.contacts]
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self, path: str | Path) -> None:
        """Replace the current contents with the book stored at `path`."""
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError(f"{path}: expected a JSON array of contacts")

        contacts: list[Contact] = []
        for i, item in enumerate(raw):
            try:
                contacts.append(Contact(**item))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}: invalid contact at position {i}: {exc}") from exc

        self.contacts = contacts
