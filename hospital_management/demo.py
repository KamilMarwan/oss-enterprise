"""Demonstration script for the hospital management system."""

from datetime import datetime

from .models import Patient, Role, User, UnitType
from .system import HospitalManagementSystem


def build_demo_system() -> HospitalManagementSystem:
    system = HospitalManagementSystem.with_default_policy()

    system.add_user(User(user_id="admin1", name="Alice", role=Role.ADMIN))
    system.add_user(User(user_id="doc1", name="Dr. Kim", role=Role.DOCTOR))
    system.add_user(User(user_id="nurse1", name="Nurse Lee", role=Role.NURSE))
    system.add_user(User(user_id="pharm1", name="Pharmacist Jones", role=Role.PHARMACIST))
    system.add_user(User(user_id="acct1", name="Accountant Sam", role=Role.ACCOUNTANT))
    system.add_user(User(user_id="clerk1", name="Records Clerk", role=Role.RECORDS_CLERK))

    patient = Patient(patient_id="p001", name="Jamie Doe", date_of_birth=datetime(1990, 5, 1))
    system.register_patient(patient)

    visit = system.start_visit(visit_id="v001", patient_id=patient.patient_id, user_id="clerk1")
    system.record_service(visit.visit_id, description="Triage and vitals", unit=UnitType.NURSING, cost=20.0, user_id="nurse1")
    system.record_service(visit.visit_id, description="Eye screening", unit=UnitType.EYE, cost=45.0, user_id="doc1")
    system.record_service(
        visit.visit_id, description="Family planning counseling", unit=UnitType.FAMILY_PLANNING, cost=30.0, user_id="doc1"
    )
    system.record_medication(
        visit.visit_id,
        medication="Prenatal vitamins",
        dosage="1 tablet daily",
        quantity=30,
        unit=UnitType.PHARMACY,
        cost=12.0,
        user_id="pharm1",
    )

    invoice = system.create_invoice(invoice_id="inv-001", visit_id=visit.visit_id, user_id="acct1")
    system.record_payment(invoice.invoice_id, amount=50.0, user_id="acct1")

    return system


def main() -> None:
    system = build_demo_system()

    print("Units:", ", ".join(system.list_units()))
    print("Roles:", ", ".join(system.list_roles()))

    summary = system.get_visit_summary("v001")
    print("\nVisit Summary")
    for key, value in summary.items():
        print(f"- {key}: {value}")

    print("\nRevenue by unit:")
    for unit in (UnitType.NURSING, UnitType.EYE, UnitType.FAMILY_PLANNING, UnitType.PHARMACY):
        report = system.report_by_unit(unit)
        print(f"- {report['unit']}: ${report['total_revenue']} from {report['services_rendered']} services")

    invoice = system.invoices["inv-001"]
    print("\nInvoice status:")
    print(f"- Total due: ${invoice.total_due}")
    print(f"- Balance: ${invoice.balance}")
    print(f"- Paid: {invoice.paid}")


if __name__ == "__main__":
    main()
