from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from app.core.constants import EmployeeStatus, UserRole


@dataclass
class Employee:
    """A staff member (may or may not have a login User account)."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    full_name: str = ""
    position: UserRole = UserRole.WAITER
    phone: str = ""
    salary: Decimal = Decimal("0.00")
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hired_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self) -> None:
        self.salary = Decimal(str(self.salary))
        if isinstance(self.position, str):
            self.position = UserRole(self.position)
        if isinstance(self.status, str):
            self.status = EmployeeStatus(self.status)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["salary"] = str(self.salary)
        data["position"] = self.position.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        data = data.copy()
        data["salary"] = Decimal(str(data["salary"]))
        if isinstance(data.get("position"), str):
            data["position"] = UserRole(data["position"])
        if isinstance(data.get("status"), str):
            data["status"] = EmployeeStatus(data["status"])
        return cls(**data)
