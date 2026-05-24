"""
sample_data/create_sample_db.py
Creates a realistic healthcare-style SQLite database for demo purposes.
Tables: patients, providers, encounters, diagnoses, medications, claims

Run: python sample_data/create_sample_db.py
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "healthcare_sample.db")

random.seed(42)

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "William", "Barbara", "Aisha", "Carlos", "Priya", "Wei", "Fatima", "Arjun"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Wilson", "Taylor", "Patel", "Kim", "Nguyen", "Chen", "Martinez", "Singh"]
STATES = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
SPECIALTIES = ["Internal Medicine", "Cardiology", "Oncology", "Neurology", "Pediatrics",
               "Emergency Medicine", "Family Medicine", "Radiology", "Orthopedics"]
ICD_CODES = {
    "I10": "Hypertension", "E11": "Type 2 Diabetes", "J45": "Asthma",
    "M54": "Back Pain", "F41": "Anxiety Disorder", "I25": "Coronary Artery Disease",
    "N18": "Chronic Kidney Disease", "J18": "Pneumonia", "K21": "GERD",
    "G43": "Migraine"
}
MEDICATIONS = [
    ("Metformin", "500mg", "Oral"), ("Lisinopril", "10mg", "Oral"),
    ("Atorvastatin", "40mg", "Oral"), ("Albuterol", "2.5mg", "Inhaled"),
    ("Aspirin", "81mg", "Oral"), ("Omeprazole", "20mg", "Oral"),
    ("Amlodipine", "5mg", "Oral"), ("Sertraline", "50mg", "Oral"),
]
ENCOUNTER_TYPES = ["Outpatient", "Inpatient", "Emergency", "Telehealth", "Preventive"]


def random_date(start_year=2020, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")


def create_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── DDL ─────────────────────────────────────────────────────────────────

    cur.executescript("""
    CREATE TABLE providers (
        provider_id     TEXT PRIMARY KEY,
        full_name       TEXT NOT NULL,
        specialty       TEXT NOT NULL,
        npi_number      TEXT UNIQUE NOT NULL,
        state           TEXT NOT NULL,
        active          INTEGER NOT NULL DEFAULT 1,
        hired_date      TEXT NOT NULL
    );

    CREATE TABLE patients (
        patient_id      TEXT PRIMARY KEY,
        first_name      TEXT NOT NULL,
        last_name       TEXT NOT NULL,
        date_of_birth   TEXT NOT NULL,
        gender          TEXT CHECK(gender IN ('M','F','O')),
        state           TEXT NOT NULL,
        zip_code        TEXT,
        insurance_type  TEXT CHECK(insurance_type IN ('Medicare','Medicaid','Commercial','Self-Pay')),
        created_at      TEXT NOT NULL,
        is_active       INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE encounters (
        encounter_id        TEXT PRIMARY KEY,
        patient_id          TEXT NOT NULL REFERENCES patients(patient_id),
        provider_id         TEXT NOT NULL REFERENCES providers(provider_id),
        encounter_date      TEXT NOT NULL,
        encounter_type      TEXT NOT NULL,
        admission_date      TEXT,
        discharge_date      TEXT,
        facility_name       TEXT NOT NULL,
        chief_complaint     TEXT,
        discharge_status    TEXT
    );

    CREATE TABLE diagnoses (
        diagnosis_id    TEXT PRIMARY KEY,
        encounter_id    TEXT NOT NULL REFERENCES encounters(encounter_id),
        icd_code        TEXT NOT NULL,
        description     TEXT NOT NULL,
        diagnosis_type  TEXT CHECK(diagnosis_type IN ('Primary','Secondary','Tertiary')),
        diagnosed_date  TEXT NOT NULL
    );

    CREATE TABLE medications (
        medication_id   TEXT PRIMARY KEY,
        encounter_id    TEXT NOT NULL REFERENCES encounters(encounter_id),
        drug_name       TEXT NOT NULL,
        dosage          TEXT NOT NULL,
        route           TEXT NOT NULL,
        prescribed_date TEXT NOT NULL,
        end_date        TEXT,
        is_active       INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE claims (
        claim_id        TEXT PRIMARY KEY,
        encounter_id    TEXT NOT NULL REFERENCES encounters(encounter_id),
        patient_id      TEXT NOT NULL REFERENCES patients(patient_id),
        claim_date      TEXT NOT NULL,
        billed_amount   REAL NOT NULL,
        allowed_amount  REAL,
        paid_amount     REAL,
        claim_status    TEXT CHECK(claim_status IN ('Submitted','Approved','Denied','Pending','Appealed')),
        denial_reason   TEXT
    );
    """)

    # ── Seed Data ────────────────────────────────────────────────────────────

    # Providers (50)
    providers = []
    for i in range(1, 51):
        pid = f"PRV{i:04d}"
        name = f"Dr. {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        providers.append((
            pid, name, random.choice(SPECIALTIES),
            f"NPI{random.randint(1000000000, 9999999999)}",
            random.choice(STATES), random.randint(0, 1), random_date(2010, 2022)
        ))
    cur.executemany("INSERT INTO providers VALUES (?,?,?,?,?,?,?)", providers)

    # Patients (500)
    patients = []
    for i in range(1, 501):
        pat_id = f"PAT{i:06d}"
        dob = random_date(1940, 2005)
        patients.append((
            pat_id, random.choice(FIRST_NAMES), random.choice(LAST_NAMES),
            dob, random.choice(["M", "F", "O"]), random.choice(STATES),
            str(random.randint(10000, 99999)),
            random.choice(["Medicare", "Medicaid", "Commercial", "Self-Pay"]),
            random_date(2018, 2020), 1
        ))
    cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?)", patients)

    # Encounters (1500)
    encounters = []
    for i in range(1, 1501):
        enc_id = f"ENC{i:07d}"
        pat_id = f"PAT{random.randint(1, 500):06d}"
        prv_id = f"PRV{random.randint(1, 50):04d}"
        enc_date = random_date()
        enc_type = random.choice(ENCOUNTER_TYPES)
        adm = enc_date if enc_type == "Inpatient" else None
        dsc = random_date(2020, 2024) if enc_type == "Inpatient" else None
        encounters.append((
            enc_id, pat_id, prv_id, enc_date, enc_type, adm, dsc,
            f"{random.choice(['City', 'Regional', 'University'])} Medical Center",
            random.choice(["Chest pain", "Shortness of breath", "Annual checkup", "Follow-up", "Fever", None]),
            random.choice(["Routine discharge", "Transfer", "AMA", None]) if enc_type == "Inpatient" else None
        ))
    cur.executemany("INSERT INTO encounters VALUES (?,?,?,?,?,?,?,?,?,?)", encounters)

    # Diagnoses (2500)
    diagnoses = []
    icd_items = list(ICD_CODES.items())
    for i in range(1, 2501):
        enc_id = f"ENC{random.randint(1, 1500):07d}"
        icd, desc = random.choice(icd_items)
        diagnoses.append((
            f"DX{i:07d}", enc_id, icd, desc,
            random.choice(["Primary", "Secondary", "Tertiary"]),
            random_date()
        ))
    cur.executemany("INSERT INTO diagnoses VALUES (?,?,?,?,?,?)", diagnoses)

    # Medications (2000)
    meds = []
    for i in range(1, 2001):
        enc_id = f"ENC{random.randint(1, 1500):07d}"
        drug, dose, route = random.choice(MEDICATIONS)
        presc_date = random_date()
        end_date = random_date(2021, 2025) if random.random() > 0.4 else None
        meds.append((f"MED{i:07d}", enc_id, drug, dose, route, presc_date, end_date, random.randint(0, 1)))
    cur.executemany("INSERT INTO medications VALUES (?,?,?,?,?,?,?,?)", meds)

    # Claims (1800)
    claims = []
    statuses = ["Submitted", "Approved", "Denied", "Pending", "Appealed"]
    denial_reasons = ["Not medically necessary", "Out of network", "Missing documentation", None, None, None]
    for i in range(1, 1801):
        enc_id = f"ENC{random.randint(1, 1500):07d}"
        pat_id = f"PAT{random.randint(1, 500):06d}"
        billed = round(random.uniform(150, 85000), 2)
        status = random.choice(statuses)
        allowed = round(billed * random.uniform(0.4, 0.95), 2) if status == "Approved" else None
        paid = round(allowed * random.uniform(0.8, 1.0), 2) if allowed else None
        denial = random.choice(denial_reasons) if status == "Denied" else None
        claims.append((f"CLM{i:07d}", enc_id, pat_id, random_date(), billed, allowed, paid, status, denial))
    cur.executemany("INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?)", claims)

    conn.commit()
    conn.close()

    print(f"✅ Sample database created: {DB_PATH}")
    print("   Tables: patients (500), providers (50), encounters (1500),")
    print("           diagnoses (2500), medications (2000), claims (1800)")


if __name__ == "__main__":
    create_database()
