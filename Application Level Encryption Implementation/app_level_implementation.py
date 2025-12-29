import psycopg2
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
f = Fernet(key)

# Database connection parameters (connection parameters may differ)
conn_params = {
    'dbname': 'encryption_test',
    'user': 'postgres',
    'password': 'postgrepw',  
    'host': 'localhost',
    'port': '5432'
}

# Function to encrypt text
def encrypt_text(text):
    return f.encrypt(text.encode()).decode()

# Function to decrypt text
def decrypt_text(encrypted_text):
    return f.decrypt(encrypted_text.encode()).decode()

# Function to insert encrypted patient record to the database
def insert_encrypted_patient(id, name, dob, icn, condition, prescription):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    # Encrypt selected sensitive fields
    encrypted_icn = encrypt_text(icn)
    encrypted_condition = encrypt_text(condition)
    encrypted_prescription = encrypt_text(prescription)
    
    # Insert encrypted patient record into database
    cur.execute("""
        INSERT INTO patients_app_encryption 
        (patient_id, name, date_of_birth, identification_card_no, medical_condition, prescription)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id, name, dob, encrypted_icn, encrypted_condition, encrypted_prescription))
    
    conn.commit()
    cur.close()
    conn.close()

# Function to retrieve patient record from the database
def retrieve_decrypted_patient(patient_id):
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT patient_id, name, date_of_birth, identification_card_no, medical_condition, prescription
        FROM patients_app_encryption
        WHERE patient_id = %s
    """, (patient_id,))
    
    row = cur.fetchone()
    
    if row:
        decrypted_data = {
            'id': row[0],
            'name': row[1],
            'dob': row[2],
            'icn': decrypt_text(row[3]),
            'condition': decrypt_text(row[4]),
            'prescription': decrypt_text(row[5])

        }
        cur.close()
        conn.close()
        return decrypted_data
    
    cur.close()
    conn.close()
    return None

# Test inserting and retrieving patient record
if __name__ == "__main__":
    insert_encrypted_patient(
        '999',
        'Aaron Aw',
        '1967-06-17',
        '670617021573',
        'Asthma',
        'Salbutamol inhaler'
    )
    
    print("Data inserted.")
    
    patient = retrieve_decrypted_patient(999)
    if patient:
        print(f"Retrieved patient: {patient}")
