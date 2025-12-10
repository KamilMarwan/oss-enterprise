from __future__ import annotations

from typing import Dict, Iterable, Mapping, Set

from .models import Role, UnitType


class AccessControl:
    """Simple role-based access control for hospital units."""

    def __init__(self, policy: Mapping[UnitType, Iterable[Role]]) -> None:
        self.policy: Dict[UnitType, Set[Role]] = {unit: set(roles) for unit, roles in policy.items()}

    def can_access(self, role: Role, unit: UnitType) -> bool:
        allowed_roles = self.policy.get(unit, set())
        return role in allowed_roles or Role.ADMIN in allowed_roles and role == Role.ADMIN

    def assert_access(self, role: Role, unit: UnitType) -> None:
        if not self.can_access(role, unit):
            raise PermissionError(f"Role {role.name} cannot access {unit.value}")
