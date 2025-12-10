from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Set


class Role(Enum):
    """Supported staff roles with different permissions."""

    ADMIN = auto()
    DOCTOR = auto()
    NURSE = auto()
    PHARMACIST = auto()
    LAB_TECH = auto()
    ACCOUNTANT = auto()
    RECORDS_CLERK = auto()


class UnitType(Enum):
    """Clinical and administrative units within the hospital."""

    RECORDS = "Records"
    REVENUE = "Revenue"
    ACCOUNTS = "Accounts"
    NURSING = "Nurses"
    WARDS = "Wards"
    MATERNITY = "Maternity"
    EYE = "Eye"
    ADOLESCENT_HEALTH = "Adolescent Reproductive Health"
    MENTAL_HEALTH = "Mental Health"
    FAMILY_PLANNING = "Family Planning"
    LABORATORY = "Laboratory"
    PHARMACY = "Pharmacy"
    DISPENSARY = "Dispensary"
    DOCTORS = "Doctors / Prescribers"


@dataclass
class User:
    """System user with a role used for access control."""

    user_id: str
    name: str
    role: Role
    assigned_units: Set[UnitType] = field(default_factory=set)


@dataclass
class Unit:
    """Represents an operational unit in the hospital."""

    unit_type: UnitType
    name: str
    services: List[str] = field(default_factory=list)


@dataclass
class Patient:
    """Basic patient record."""

    patient_id: str
    name: str
    date_of_birth: datetime
    demographics: Dict[str, str] = field(default_factory=dict)


@dataclass
class Service:
    """Clinical or administrative service provided to a patient."""

    description: str
    unit: UnitType
    cost: float


@dataclass
class MedicationOrder:
    """Medication request placed by a prescriber and filled by pharmacy or dispensary."""

    medication: str
    dosage: str
    quantity: int
    unit: UnitType
    cost: float


@dataclass
class Visit:
    """Represents a patient visit across units."""

    visit_id: str
    patient: Patient
    started_at: datetime = field(default_factory=datetime.utcnow)
    services: List[Service] = field(default_factory=list)
    medications: List[MedicationOrder] = field(default_factory=list)

    def total_cost(self) -> float:
        return sum(service.cost for service in self.services) + sum(order.cost for order in self.medications)


@dataclass
class Invoice:
    """Billing record for a visit."""

    invoice_id: str
    visit: Visit
    created_at: datetime = field(default_factory=datetime.utcnow)
    paid: bool = False
    payments: List[float] = field(default_factory=list)

    @property
    def total_due(self) -> float:
        return self.visit.total_cost()

    @property
    def balance(self) -> float:
        return self.total_due - sum(self.payments)

    def add_payment(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Payment amount cannot be negative")
        self.payments.append(amount)
        self.paid = self.balance <= 0
