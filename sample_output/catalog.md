# Data Catalog — healthcare_sample

> Generated: 2026-05-24 06:42 UTC  
> Tables: 6 | Total Rows: 8,350 | AI-powered descriptions via Ollama (llama3.2)

---

## Table of Contents


- [claims](#claims) — 1,800 rows

- [diagnoses](#diagnoses) — 2,500 rows

- [encounters](#encounters) — 1,500 rows

- [medications](#medications) — 2,000 rows

- [patients](#patients) — 500 rows

- [providers](#providers) — 50 rows


---


## claims

**1800 rows · 9 columns**

The claims table stores records related to claims. It contains 1,800 rows and 9 columns.

> 💡 **Purpose:** Stores claims data for operational and analytical use.


**Relationships:**

- `patient_id` → `patients.patient_id`

- `encounter_id` → `encounters.encounter_id`






⚠️ **Data Quality Warnings:**

- Column &#39;allowed_amount&#39; has 81.3% null values

- Column &#39;paid_amount&#39; has 81.3% null values

- Column &#39;claim_status&#39; has only 5 distinct values — consider an ENUM or CHECK constraint

- Column &#39;denial_reason&#39; has 90.7% null values

- Column &#39;denial_reason&#39; has only 3 distinct values — consider an ENUM or CHECK constraint



### Columns

| Column | Type | Nullable | Null % | Distinct | Description |
|--------|------|----------|--------|----------|-------------|
| `claim_id` 🔑 | TEXT | Yes | 0.0% | 1800 | This column uniquely identifies each claim with a unique alphanumeric identifier. |
| `encounter_id` 🔗 | TEXT | No | 0.0% | 1034 | This column uniquely identifies each encounter in a healthcare setting with a standardized identifier format. |
| `patient_id` 🔗 | TEXT | No | 0.0% | 483 | This column uniquely identifies patients in a healthcare claims database with a standardized patient ID format. |
| `claim_date` | TEXT | No | 0.0% | 1138 | The claim_date column stores dates of claims in a standardized format with year, month, and day components. |
| `billed_amount` | REAL | No | 0.0% | 1800 | The billed_amount column stores the total amount billed for a claim in dollars. |
| `allowed_amount` | REAL | Yes | 81.3% | 336 | The allowed_amount column represents the maximum amount a claimant is allowed to pay for a specific claim. |
| `paid_amount` | REAL | Yes | 81.3% | 336 | The paid_amount column records the amount of money paid out for each claim in a real value. |
| `claim_status` | TEXT | Yes | 0.0% | 5 | The claim_status column stores a textual description of the current status of a claim in the database. |
| `denial_reason` | TEXT | Yes | 90.7% | 3 | The denial_reason column stores reasons for denied claims, including medical necessity and billing-related issues. |


### Example Query

```sql
SELECT * FROM claims LIMIT 10;
```

### DDL

```sql
CREATE TABLE claims (
        claim_id        TEXT PRIMARY KEY,
        encounter_id    TEXT NOT NULL REFERENCES encounters(encounter_id),
        patient_id      TEXT NOT NULL REFERENCES patients(patient_id),
        claim_date      TEXT NOT NULL,
        billed_amount   REAL NOT NULL,
        allowed_amount  REAL,
        paid_amount     REAL,
        claim_status    TEXT CHECK(claim_status IN (&#39;Submitted&#39;,&#39;Approved&#39;,&#39;Denied&#39;,&#39;Pending&#39;,&#39;Appealed&#39;)),
        denial_reason   TEXT
    )
```

---


## diagnoses

**2500 rows · 6 columns**

The diagnoses table stores information about medical diagnoses made during patient encounters, providing a central repository for clinical data that can be used to support decision-making and quality improvement initiatives.

> 💡 **Purpose:** To provide a standardized way of capturing and managing clinical diagnosis data across the organization.


**Relationships:**

- `encounter_id` → `encounters.encounter_id`






⚠️ **Data Quality Warnings:**

- Column &#39;diagnosis_type&#39; has only 3 distinct values — consider an ENUM or CHECK constraint



### Columns

| Column | Type | Nullable | Null % | Distinct | Description |
|--------|------|----------|--------|----------|-------------|
| `diagnosis_id` 🔑 | TEXT | Yes | 0.0% | 2500 | This column uniquely identifies each diagnosis with a standardized alphanumeric code. |
| `encounter_id` 🔗 | TEXT | No | 0.0% | 1222 | This column uniquely identifies each patient encounter in the database with a unique identifier string. |
| `icd_code` | TEXT | No | 0.0% | 10 | This column stores unique International Classification of Diseases (ICD) codes for diagnoses. |
| `description` | TEXT | No | 0.0% | 10 | This column stores a brief textual description of each diagnosis in the diagnoses table. |
| `diagnosis_type` | TEXT | Yes | 0.0% | 3 | This column stores descriptive types of medical diagnoses, such as primary, secondary, and tertiary conditions. |
| `diagnosed_date` | TEXT | No | 0.0% | 1352 | The diagnosed_date column stores dates of diagnosis for patients in the database. |


### Example Query

```sql
SELECT * FROM diagnoses WHERE icd_code = &#39;I10&#39; AND diagnosis_type = &#39;Primary&#39;; -- Retrieves all primary diagnoses for patients with ICD-10 code I10.
```

### DDL

```sql
CREATE TABLE diagnoses (
        diagnosis_id    TEXT PRIMARY KEY,
        encounter_id    TEXT NOT NULL REFERENCES encounters(encounter_id),
        icd_code        TEXT NOT NULL,
        description     TEXT NOT NULL,
        diagnosis_type  TEXT CHECK(diagnosis_type IN (&#39;Primary&#39;,&#39;Secondary&#39;,&#39;Tertiary&#39;)),
        diagnosed_date  TEXT NOT NULL
    )
```

---


## encounters

**1500 rows · 10 columns**

The encounters table stores information about patient encounters with healthcare providers, including details such as encounter date, type, and facility name. It serves as a central repository for tracking patient interactions with providers, facilitating data analysis and reporting across the organization.

> 💡 **Purpose:** To track and analyze patient encounters with healthcare providers.


**Relationships:**

- `provider_id` → `providers.provider_id`

- `patient_id` → `patients.patient_id`




**Referenced by:** claims, diagnoses, medications



⚠️ **Data Quality Warnings:**

- Column &#39;encounter_type&#39; has only 5 distinct values — consider an ENUM or CHECK constraint

- Column &#39;admission_date&#39; has 80.7% null values

- Column &#39;discharge_date&#39; has 80.7% null values

- Column &#39;facility_name&#39; has only 3 distinct values — consider an ENUM or CHECK constraint

- Column &#39;chief_complaint&#39; has only 5 distinct values — consider an ENUM or CHECK constraint

- Column &#39;discharge_status&#39; has 85.5% null values

- Column &#39;discharge_status&#39; has only 3 distinct values — consider an ENUM or CHECK constraint



### Columns

| Column | Type | Nullable | Null % | Distinct | Description |
|--------|------|----------|--------|----------|-------------|
| `encounter_id` 🔑 | TEXT | Yes | 0.0% | 1500 | This column uniquely identifies each encounter with a unique alphanumeric identifier. |
| `patient_id` 🔗 | TEXT | No | 0.0% | 471 | This column uniquely identifies patients in encounters with a standardized patient ID format. |
| `provider_id` 🔗 | TEXT | No | 0.0% | 50 | This column uniquely identifies a healthcare provider by their unique ID or identifier code. |
| `encounter_date` | TEXT | No | 0.0% | 1036 | The encounter_date column stores dates of past encounters in a standardized format. |
| `encounter_type` | TEXT | No | 0.0% | 5 | This column stores the type of encounter, such as Telehealth, Preventive, or Inpatient, for each record in the encounters table. |
| `admission_date` | TEXT | Yes | 80.7% | 270 | The admission_date column stores dates of patient admissions in a human-readable format. |
| `discharge_date` | TEXT | Yes | 80.7% | 268 | The discharge_date column records the date a patient was discharged from care or treatment. |
| `facility_name` | TEXT | No | 0.0% | 3 | This column stores the names of facilities where encounters occurred, such as hospitals or medical centers. |
| `chief_complaint` | TEXT | Yes | 18.9% | 5 | The chief_complaint column captures patients&#39; primary reasons for visiting the emergency department or clinic. |
| `discharge_status` | TEXT | Yes | 85.5% | 3 | The discharge_status column records the reason for a patient&#39;s hospital discharge or departure. |


### Example Query

```sql
SELECT * FROM encounters WHERE provider_id = &#39;provider_123&#39; AND discharge_date IS NOT NULL; -- Retrieves all encounters where a specific provider was involved and the patient was discharged.
```

### DDL

```sql
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
    )
```

---


## medications

**2000 rows · 8 columns**

The medications table stores information about prescribed medications for patients, including details such as medication name, dosage, route of administration, and prescription dates. It plays a crucial role in the data model by providing a centralized repository for medication-related data, enabling efficient querying and analysis.

> 💡 **Purpose:** To store and manage medication data for clinical decision support and research purposes.


**Relationships:**

- `encounter_id` → `encounters.encounter_id`






⚠️ **Data Quality Warnings:**

- Column &#39;drug_name&#39; has only 8 distinct values — consider an ENUM or CHECK constraint

- Column &#39;dosage&#39; has only 8 distinct values — consider an ENUM or CHECK constraint

- Column &#39;route&#39; has only 2 distinct values — consider an ENUM or CHECK constraint

- Column &#39;end_date&#39; has 41.5% null values

- Column &#39;is_active&#39; has only 2 distinct values — consider an ENUM or CHECK constraint



### Columns

| Column | Type | Nullable | Null % | Distinct | Description |
|--------|------|----------|--------|----------|-------------|
| `medication_id` 🔑 | TEXT | Yes | 0.0% | 2000 | This column uniquely identifies each medication with a unique alphanumeric code. |
| `encounter_id` 🔗 | TEXT | No | 0.0% | 1107 | This column uniquely identifies each patient encounter in a healthcare setting with a standardized code. |
| `drug_name` | TEXT | No | 0.0% | 8 | This column stores unique names of medications used in clinical trials or research studies. |
| `dosage` | TEXT | No | 0.0% | 8 | The dosage column stores medication dosages as text strings in milligrams. |
| `route` | TEXT | No | 0.0% | 2 | This column stores the method by which a medication is administered to the patient. |
| `prescribed_date` | TEXT | No | 0.0% | 1204 | The prescribed_date column stores dates of medication prescription for each patient record in the database. |
| `end_date` | TEXT | Yes | 41.5% | 858 | This column stores the end date of medication prescriptions for patients in the database. |
| `is_active` | INTEGER | No | 0.0% | 2 | This column indicates whether a medication is currently active in inventory or not. |


### Example Query

```sql
SELECT m.drug_name, e.encounter_date FROM medications m JOIN encounters e ON m.encounter_id = e.encounter_id WHERE m.is_active = 1 AND e.encounter_type = &#39;office_visit&#39; ORDER BY m.prescribed_date DESC
```

### DDL

```sql
CREATE TABLE medications (
        medication_id   TEXT PRIMARY KEY,
        encounter_id    TEXT NOT NULL REFERENCES encounters(encounter_id),
        drug_name       TEXT NOT NULL,
        dosage          TEXT NOT NULL,
        route           TEXT NOT NULL,
        prescribed_date TEXT NOT NULL,
        end_date        TEXT,
        is_active       INTEGER NOT NULL DEFAULT 1
    )
```

---


## patients

**500 rows · 10 columns**

The patients table stores demographic and insurance information for individual patients, serving as a central repository for patient data in the data model.

> 💡 **Purpose:** To store and manage patient information for clinical and administrative purposes.




**Referenced by:** claims, encounters



⚠️ **Data Quality Warnings:**

- Column &#39;gender&#39; has only 3 distinct values — consider an ENUM or CHECK constraint

- Column &#39;insurance_type&#39; has only 4 distinct values — consider an ENUM or CHECK constraint

- Column &#39;is_active&#39; has only 1 distinct values — consider an ENUM or CHECK constraint



### Columns

| Column | Type | Nullable | Null % | Distinct | Description |
|--------|------|----------|--------|----------|-------------|
| `patient_id` 🔑 | TEXT | Yes | 0.0% | 500 | The patient_id column uniquely identifies each patient in the database with a unique alphanumeric identifier. |
| `first_name` | TEXT | No | 0.0% | 16 | This column stores unique identifiers for individual patients in a medical database. |
| `last_name` | TEXT | No | 0.0% | 16 | The last_name column stores unique identifiers for patients in a medical database. |
| `date_of_birth` | TEXT | No | 0.0% | 493 | The date_of_birth column stores a patient&#39;s birthdate in the format of year-month-day. |
| `gender` | TEXT | Yes | 0.0% | 3 | The patients table&#39;s gender column stores a person&#39;s biological sex as either &#39;F&#39; for female or &#39;M&#39; for male. |
| `state` | TEXT | No | 0.0% | 10 | This column stores a two-letter state abbreviation for each patient in the United States. |
| `zip_code` | TEXT | Yes | 0.0% | 498 | This column stores unique zip codes associated with individual patients in the database. |
| `insurance_type` | TEXT | Yes | 0.0% | 4 | This column stores the type of insurance coverage a patient has, such as commercial, Medicare, or self-pay. |
| `created_at` | TEXT | No | 0.0% | 408 | The created_at column stores dates in the format &#39;YYYY-MM-DD&#39; representing when each patient record was created. |
| `is_active` | INTEGER | No | 0.0% | 1 | This column indicates whether a patient&#39;s account is currently active or inactive in the system. |


### Example Query

```sql
SELECT * FROM patients WHERE state = &#39;CA&#39; AND is_active = 1; -- Retrieves all active patients from California.
```

### DDL

```sql
CREATE TABLE patients (
        patient_id      TEXT PRIMARY KEY,
        first_name      TEXT NOT NULL,
        last_name       TEXT NOT NULL,
        date_of_birth   TEXT NOT NULL,
        gender          TEXT CHECK(gender IN (&#39;M&#39;,&#39;F&#39;,&#39;O&#39;)),
        state           TEXT NOT NULL,
        zip_code        TEXT,
        insurance_type  TEXT CHECK(insurance_type IN (&#39;Medicare&#39;,&#39;Medicaid&#39;,&#39;Commercial&#39;,&#39;Self-Pay&#39;)),
        created_at      TEXT NOT NULL,
        is_active       INTEGER NOT NULL DEFAULT 1
    )
```

---


## providers

**50 rows · 7 columns**

The providers table stores information about healthcare professionals, including their full name, specialty, NPI number, state of licensure, and hire date. This data is used to support various business processes and analytics in the healthcare industry.

> 💡 **Purpose:** To provide a centralized repository for provider information, enabling efficient querying and analysis across the organization.




**Referenced by:** encounters



⚠️ **Data Quality Warnings:**

- Column &#39;specialty&#39; has only 9 distinct values — consider an ENUM or CHECK constraint

- Column &#39;active&#39; has only 2 distinct values — consider an ENUM or CHECK constraint



### Columns

| Column | Type | Nullable | Null % | Distinct | Description |
|--------|------|----------|--------|----------|-------------|
| `provider_id` 🔑 | TEXT | Yes | 0.0% | 50 | This column uniquely identifies each provider with a unique alphanumeric identifier. |
| `full_name` | TEXT | No | 0.0% | 48 | This column stores unique full names of healthcare providers with no duplicates allowed. |
| `specialty` | TEXT | No | 0.0% | 9 | This column stores unique specialty names for each provider in the database. |
| `npi_number` | TEXT | No | 0.0% | 50 | The npi_number column uniquely identifies healthcare providers with a unique National Provider Identifier number. |
| `state` | TEXT | No | 0.0% | 10 | This column stores unique two-letter state abbreviations for healthcare providers in the United States. |
| `active` | INTEGER | No | 0.0% | 2 | This column indicates whether a provider is currently active or not in the database. |
| `hired_date` | TEXT | No | 0.0% | 50 | The hired_date column stores dates when providers were hired, in YYYY-MM-DD format. |


### Example Query

```sql
SELECT * FROM providers WHERE active = 1 AND specialty = &#39;Primary Care&#39; ORDER BY hired_date DESC; -- Retrieves all primary care providers who are currently active, listed in reverse chronological order by hire date.
```

### DDL

```sql
CREATE TABLE providers (
        provider_id     TEXT PRIMARY KEY,
        full_name       TEXT NOT NULL,
        specialty       TEXT NOT NULL,
        npi_number      TEXT UNIQUE NOT NULL,
        state           TEXT NOT NULL,
        active          INTEGER NOT NULL DEFAULT 1,
        hired_date      TEXT NOT NULL
    )
```

---



*Generated by [data-dict-generator](https://github.com/YOUR_USERNAME/data-dict-generator) — Aritra Ghorai*