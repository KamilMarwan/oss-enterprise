from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .access import AccessControl
from .models import Invoice, MedicationOrder, Patient, Role, Service, Unit, UnitType, User, Visit


@dataclass
class HospitalManagementSystem:
    """In-memory hospital management system with role-based access control."""

    access_control: AccessControl
    users: Dict[str, User] = field(default_factory=dict)
    units: Dict[UnitType, Unit] = field(default_factory=dict)
    patients: Dict[str, Patient] = field(default_factory=dict)
    visits: Dict[str, Visit] = field(default_factory=dict)
    invoices: Dict[str, Invoice] = field(default_factory=dict)

    def add_user(self, user: User) -> None:
        self.users[user.user_id] = user

    def register_unit(self, unit: Unit) -> None:
        self.units[unit.unit_type] = unit

    def register_patient(self, patient: Patient) -> None:
        self.patients[patient.patient_id] = patient

    def start_visit(self, visit_id: str, patient_id: str, user_id: str) -> Visit:
        user = self.users[user_id]
        self.access_control.assert_access(user.role, UnitType.RECORDS)
        patient = self.patients[patient_id]
        visit = Visit(visit_id=visit_id, patient=patient)
        self.visits[visit_id] = visit
        return visit

    def record_service(self, visit_id: str, description: str, unit: UnitType, cost: float, user_id: str) -> Service:
        user = self.users[user_id]
        self.access_control.assert_access(user.role, unit)
        visit = self.visits[visit_id]
        service = Service(description=description, unit=unit, cost=cost)
        visit.services.append(service)
        return service

    def record_medication(
        self, visit_id: str, medication: str, dosage: str, quantity: int, unit: UnitType, cost: float, user_id: str
    ) -> MedicationOrder:
        user = self.users[user_id]
        if unit not in (UnitType.PHARMACY, UnitType.DISPENSARY):
            raise ValueError("Medication must be recorded in Pharmacy or Dispensary units")
        self.access_control.assert_access(user.role, unit)
        visit = self.visits[visit_id]
        order = MedicationOrder(medication=medication, dosage=dosage, quantity=quantity, unit=unit, cost=cost)
        visit.medications.append(order)
        return order

    def create_invoice(self, invoice_id: str, visit_id: str, user_id: str) -> Invoice:
        user = self.users[user_id]
        self.access_control.assert_access(user.role, UnitType.REVENUE)
        visit = self.visits[visit_id]
        invoice = Invoice(invoice_id=invoice_id, visit=visit)
        self.invoices[invoice_id] = invoice
        return invoice

    def record_payment(self, invoice_id: str, amount: float, user_id: str) -> Invoice:
        user = self.users[user_id]
        self.access_control.assert_access(user.role, UnitType.ACCOUNTS)
        invoice = self.invoices[invoice_id]
        invoice.add_payment(amount)
        return invoice

    def get_visit_summary(self, visit_id: str) -> Dict[str, object]:
        visit = self.visits[visit_id]
        return {
            "patient": visit.patient.name,
            "services": [service.description for service in visit.services],
            "medications": [order.medication for order in visit.medications],
            "total_cost": visit.total_cost(),
        }

    def report_by_unit(self, unit: UnitType) -> Dict[str, float]:
        """Aggregate revenue for services performed by a unit."""

        total = 0.0
        service_count = 0
        for visit in self.visits.values():
            for service in visit.services:
                if service.unit == unit:
                    total += service.cost
                    service_count += 1
        return {"unit": unit.value, "total_revenue": total, "services_rendered": service_count}

    @classmethod
    def with_default_policy(cls) -> "HospitalManagementSystem":
        policy = {
            UnitType.RECORDS: {Role.ADMIN, Role.RECORDS_CLERK},
            UnitType.REVENUE: {Role.ADMIN, Role.ACCOUNTANT},
            UnitType.ACCOUNTS: {Role.ADMIN, Role.ACCOUNTANT},
            UnitType.NURSING: {Role.ADMIN, Role.NURSE},
            UnitType.WARDS: {Role.ADMIN, Role.NURSE},
            UnitType.MATERNITY: {Role.ADMIN, Role.NURSE, Role.DOCTOR},
            UnitType.EYE: {Role.ADMIN, Role.DOCTOR},
            UnitType.ADOLESCENT_HEALTH: {Role.ADMIN, Role.DOCTOR, Role.NURSE},
            UnitType.MENTAL_HEALTH: {Role.ADMIN, Role.DOCTOR},
            UnitType.FAMILY_PLANNING: {Role.ADMIN, Role.DOCTOR, Role.NURSE},
            UnitType.LABORATORY: {Role.ADMIN, Role.LAB_TECH},
            UnitType.PHARMACY: {Role.ADMIN, Role.PHARMACIST},
            UnitType.DISPENSARY: {Role.ADMIN, Role.PHARMACIST},
            UnitType.DOCTORS: {Role.ADMIN, Role.DOCTOR},
        }
        system = cls(access_control=AccessControl(policy=policy))
        for unit_type in UnitType:
            system.register_unit(Unit(unit_type=unit_type, name=unit_type.value))
        return system

    def assign_user_to_unit(self, user_id: str, unit: UnitType) -> None:
        user = self.users[user_id]
        user.assigned_units.add(unit)

    def find_patient(self, patient_id: str) -> Optional[Patient]:
        return self.patients.get(patient_id)

    def list_units(self) -> List[str]:
        return [unit.value for unit in UnitType]

    def list_roles(self) -> List[str]:
        return [role.name for role in Role]
