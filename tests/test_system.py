from datetime import datetime

import pytest

from hospital_management.models import Patient, Role, UnitType, User
from hospital_management.system import HospitalManagementSystem


def build_system():
    system = HospitalManagementSystem.with_default_policy()
    system.add_user(User(user_id="clerk", name="Records", role=Role.RECORDS_CLERK))
    system.add_user(User(user_id="doctor", name="Doctor", role=Role.DOCTOR))
    system.add_user(User(user_id="nurse", name="Nurse", role=Role.NURSE))
    system.add_user(User(user_id="labtech", name="Lab Tech", role=Role.LAB_TECH))
    system.add_user(User(user_id="pharm", name="Pharmacist", role=Role.PHARMACIST))
    system.add_user(User(user_id="accountant", name="Accountant", role=Role.ACCOUNTANT))

    patient = Patient(patient_id="p1", name="Test Patient", date_of_birth=datetime(1990, 1, 1))
    system.register_patient(patient)
    return system, patient


def test_visit_and_invoice_flow():
    system, patient = build_system()

    visit = system.start_visit("v1", patient.patient_id, user_id="clerk")
    system.record_service(visit.visit_id, "Ward admission", UnitType.WARDS, 100.0, user_id="nurse")
    system.record_service(visit.visit_id, "Doctor consult", UnitType.DOCTORS, 75.0, user_id="doctor")
    system.record_medication(visit.visit_id, "Painkiller", "10mg", 10, UnitType.PHARMACY, 20.0, user_id="pharm")

    invoice = system.create_invoice("inv1", visit.visit_id, user_id="accountant")
    assert invoice.total_due == pytest.approx(195.0)

    system.record_payment(invoice.invoice_id, 195.0, user_id="accountant")
    assert invoice.paid
    assert invoice.balance == pytest.approx(0.0)


def test_permission_enforced():
    system, patient = build_system()
    system.start_visit("v1", patient.patient_id, user_id="clerk")

    with pytest.raises(PermissionError):
        system.create_invoice("inv1", "v1", user_id="doctor")


def test_report_by_unit():
    system, patient = build_system()
    visit = system.start_visit("v1", patient.patient_id, user_id="clerk")
    system.record_service(visit.visit_id, "Lab test", UnitType.LABORATORY, 40.0, user_id="labtech")
    system.record_service(visit.visit_id, "Family planning", UnitType.FAMILY_PLANNING, 25.0, user_id="doctor")

    lab_report = system.report_by_unit(UnitType.LABORATORY)
    assert lab_report["total_revenue"] == pytest.approx(40.0)
    assert lab_report["services_rendered"] == 1

    fp_report = system.report_by_unit(UnitType.FAMILY_PLANNING)
    assert fp_report["total_revenue"] == pytest.approx(25.0)
