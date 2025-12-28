-- Keyring file configuration following instructions from official website https://docs.percona.com/pg-tde/global-key-provider-configuration/keyring.html

SELECT pg_tde_add_database_key_provider_file(
    'test-provider',
    '/tmp/pg_tde_test_local_keyring.per'
);

SELECT pg_tde_create_key_using_database_key_provider(
    'default_tde_key',
    'test-provider'
);

SELECT pg_tde_set_key_using_database_key_provider(
    'default_tde_key',
    'test-provider'
);

-- Create table encrypted with TDE  
CREATE TABLE patients_tde (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    date_of_birth DATE,
    identification_card_no VARCHAR(12),
    medical_condition VARCHAR(255),
    prescription VARCHAR(255)
) USING tde_heap;

-- Verify if table is encrypted 
SELECT pg_tde_is_encrypted('patients_tde'); 
-- Returns t indicating table is encrypted with TDE

-- Test inserting values into table
INSERT INTO patients_tde(patient_id, name, date_of_birth, identification_card_no, medical_condition, prescription) VALUES(999, 'Aaron Aw', '1967-06-17', 670617021573, 'Asthma', 'Salbutamol inhaler');
