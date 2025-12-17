-- Table for baseline with no encryption
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no VARCHAR(12),
    medical_condition VARCHAR(255),
    prescription VARCHAR(255)
);

-- Table for column level encryption implementation
CREATE TABLE patients_column_encryption (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no BYTEA,
    medical_condition BYTEA,
    prescription BYTEA
);

-- Table for application level encryption implementation
CREATE TABLE patients_app_encryption (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no VARCHAR(12),
    medical_condition VARCHAR(255),
    prescription VARCHAR(255)
);

-- Table for transparent data encryption (TDE) implementation
CREATE TABLE patients_tde (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no VARCHAR(12),
    medical_condition VARCHAR(255),
    prescription VARCHAR(255)
);
