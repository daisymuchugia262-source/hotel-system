from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from app.core.constants import UserRole


@dataclass
class User:
    """A system user (staff member who can log in)."""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.WAITER
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        if self.username and len(self.username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email address")
        if isinstance(self.role, str):
            self.role = UserRole(self.role)

    def to_dict(self, include_hash: bool = False) -> dict:
        data = asdict(self)
        data["role"] = self.role.value
        if not include_hash:
            data.pop("password_hash", None)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        data = data.copy()
        if isinstance(data.get("role"), str):
            data["role"] = UserRole(data["role"])
        return cls(**data)
