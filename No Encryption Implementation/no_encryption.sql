-- Table for baseline with no encryption
CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no VARCHAR(12),
    medical_condition VARCHAR(255),
    prescription VARCHAR(255)
);

-- Insert test data to table
INSERT INTO patients(patient_id, name, date_of_birth, identification_card_no, medical_condition, prescription) 
VALUES(999, 'Aaron Aw', '1967-06-17', 670617021573, 'Asthma', 'Salbutamol inhaler');
