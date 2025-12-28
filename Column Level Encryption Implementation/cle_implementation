-- Create table for column level encryption implementation
CREATE TABLE patients_column_encryption (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no BYTEA,
    medical_condition BYTEA,
    prescription BYTEA
);

-- Install pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Function to encrypt data for Column Level Encryption
CREATE OR REPLACE FUNCTION encrypt_data(data TEXT, key TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, key);
END;
$$ LANGUAGE plpgsql;

-- Function to decrypt data for Column Level Encryption
CREATE OR REPLACE FUNCTION decrypt_data(encrypted_data BYTEA, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_data, key);
END;
$$ LANGUAGE plpgsql;

-- Insert test data to the table with column level encryption
INSERT INTO patients_column_encryption 
    (patient_id, name, date_of_birth, identification_card_no, medical_condition, prescription)
VALUES 
    ( 999,
	 'Aaron Aw', 
     '1967-06-17', 
     encrypt_data('670617021573', 'test_key'),
     encrypt_data('Asthma', 'test_key'),
     encrypt_data('Salbutamol inhaler', 'test_key'));

-- Query encrypted data
SELECT 
    patient_id,
    name,
	date_of_birth,
    decrypt_data(identification_card_no, 'test_key') AS icn,
    decrypt_data(medical_condition, 'test_key') AS condition,
    decrypt_data(prescription, 'test_key') AS prescription
FROM patients_column_encryption;
