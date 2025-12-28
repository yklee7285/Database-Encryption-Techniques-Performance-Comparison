import psycopg2
import time
import csv
from cryptography.fernet import Fernet
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Connection parameters for Windows PostgreSQL
conn_params_windows = {
    'dbname': 'encryption_test',
    'user': 'postgres',
    'password': '9874darius',  
    'host': 'localhost',
    'port': '5432'
}

# Connection parameters for WSL PostgreSQL
conn_params_wsl = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '9874darius',  
    'host': 'localhost',
    'port': '5433'
}

# Function to reset database session state
def reset_session_state():
    # For Windows PostgreSQL
    conn = psycopg2.connect(**conn_params_windows)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DISCARD ALL") 
    conn.commit()
    cur.close()
    conn.close()

    # For WSL PostgreSQL
    conn = psycopg2.connect(**conn_params_wsl)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DISCARD ALL")
    conn.commit()
    cur.close()
    conn.close()
    
    time.sleep(1)

# Encryption keys
column_encryption_key = 'performance_test_key'
key = Fernet.generate_key()
f = Fernet(key)

# CSV file path
CSV_FILE_PATH = 'patient_data.csv'

# Test configuration
TEST_SIZES = [25, 50, 75, 100]


# Load patient data from CSV file
def load_patient_data(limit=None):
    from datetime import datetime    

    patients = []

    with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Convert date format from DD/MM/YYYY to YYYY-MM-DD
            dob = row['date_of_birth']
            try:
                if '/' in dob:
                    date_obj = datetime.strptime(dob, '%d/%m/%Y')
                    formatted_dob = date_obj.strftime('%Y-%m-%d')
                elif '-' in dob and dob.count('-') == 2:
                    parts = dob.split('-')
                    if len(parts[0]) <= 2: 
                        date_obj = datetime.strptime(dob, '%d-%m-%Y')
                        formatted_dob = date_obj.strftime('%Y-%m-%d')
                    else:  
                        formatted_dob = dob
                else:
                    formatted_dob = dob
            except:
                formatted_dob = dob
            
            patients.append({
                'patient_id': int(row['patient_id']),
                'name': row['name'],
                'date_of_birth': formatted_dob,
                'identification_card_no': str(row['identification_card_no']),
                'medical_condition': row['medical_condition'],
                'prescription': row['prescription']
            })
            if limit and len(patients) >= limit:
                break
    return patients

# Function to test performance of  no encryption
def test_no_encryption(num_records):
    print(f"Testing No Encryption ({num_records} records)")
    
    conn = psycopg2.connect(**conn_params_windows)
    cur = conn.cursor()
    
    # Load data
    patients = load_patient_data(limit=num_records)
    
    # Clear table
    cur.execute("TRUNCATE patients RESTART IDENTITY CASCADE")
    conn.commit()
    
    # INSERT test
    start = time.time()
    for p in patients:
        cur.execute("""
            INSERT INTO patients 
            (patient_id, name, date_of_birth, identification_card_no, 
             medical_condition, prescription)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (p['patient_id'], p['name'], p['date_of_birth'],
              p['identification_card_no'], p['medical_condition'], p['prescription']))
    conn.commit()
    insert_time = time.time() - start
    
    # SELECT test
    start = time.time()
    cur.execute(f"SELECT * FROM patients")
    results = cur.fetchall()
    select_time = time.time() - start
    
    # UPDATE test (update 10 records)
    start = time.time()
    for i in range(1, num_records + 1):
        cur.execute("UPDATE patients SET medical_condition = 'Updated Condition' WHERE patient_id = %s", (i,))
    conn.commit()
    update_time = time.time() - start
    
    cur.close()
    conn.close()
    
    print(f"INSERT: {insert_time:.4f}s | SELECT: {select_time:.4f}s | UPDATE: {update_time:.4f}s")
    return {'insert': insert_time, 'select': select_time, 'update': update_time}

# Function to test performance of column level encryption
def test_column_encryption(num_records):
    print(f"Testing Column Level Encryption ({num_records} records)")
    
    conn = psycopg2.connect(**conn_params_windows)
    cur = conn.cursor()
    
    # Load data
    patients = load_patient_data(limit=num_records)
    
    # Clear table
    cur.execute("TRUNCATE patients_column_encryption RESTART IDENTITY CASCADE")
    conn.commit()
    
    # INSERT test
    start = time.time()
    for p in patients:
        cur.execute("""
            INSERT INTO patients_column_encryption 
            (patient_id, name, date_of_birth, identification_card_no,
             medical_condition, prescription)
            VALUES (%s, %s, %s,
                    pgp_sym_encrypt(%s, %s),
                    pgp_sym_encrypt(%s, %s),
                    pgp_sym_encrypt(%s, %s))
        """, (p['patient_id'], p['name'], p['date_of_birth'],
              p['identification_card_no'], column_encryption_key,
              p['medical_condition'], column_encryption_key,
              p['prescription'], column_encryption_key))
    conn.commit()
    insert_time = time.time() - start
    
    # SELECT test 
    start = time.time()
    cur.execute("""
        SELECT patient_id, name, date_of_birth,
               pgp_sym_decrypt(identification_card_no, %s),
               pgp_sym_decrypt(medical_condition, %s),
               pgp_sym_decrypt(prescription, %s)
        FROM patients_column_encryption
    """, (column_encryption_key, column_encryption_key, column_encryption_key))
    results = cur.fetchall()
    select_time = time.time() - start
    
    # UPDATE test
    start = time.time()
    for i in range(1, num_records + 1):
        cur.execute("""
            UPDATE patients_column_encryption 
            SET medical_condition = pgp_sym_encrypt(%s, %s)
            WHERE patient_id = %s
        """, ('Updated Condition', column_encryption_key, i))
    conn.commit()
    update_time = time.time() - start
    
    cur.close()
    conn.close()
    
    print(f"INSERT: {insert_time:.4f}s | SELECT: {select_time:.4f}s | UPDATE: {update_time:.4f}s")
    return {'insert': insert_time, 'select': select_time, 'update': update_time}

# Function to test performance of application level encryption
def test_app_encryption(num_records):
    print(f"Testing Application Encryption ({num_records} records)")
    
    conn = psycopg2.connect(**conn_params_windows)
    cur = conn.cursor()
    
    # Load data
    patients = load_patient_data(limit=num_records)
    
    # Clear table
    cur.execute("TRUNCATE patients_app_encryption RESTART IDENTITY CASCADE")
    conn.commit()
    
    # INSERT test
    start = time.time()
    for p in patients:
        enc_icn = f.encrypt(p['identification_card_no'].encode()).decode()
        enc_condition = f.encrypt(p['medical_condition'].encode()).decode()
        enc_prescription = f.encrypt(p['prescription'].encode()).decode()
        
        cur.execute("""
            INSERT INTO patients_app_encryption 
            (patient_id, name, date_of_birth, identification_card_no,
             medical_condition, prescription)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (p['patient_id'], p['name'], p['date_of_birth'],
              enc_icn, enc_condition, enc_prescription))
    conn.commit()
    insert_time = time.time() - start
    
    # SELECT test 
    start = time.time()
    cur.execute("SELECT * FROM patients_app_encryption")
    results = cur.fetchall()
    for row in results:
        dec_icn = f.decrypt(row[3].encode()).decode()
        dec_condition = f.decrypt(row[4].encode()).decode()
        dec_prescription = f.decrypt(row[5].encode()).decode()
    select_time = time.time() - start
    
    # UPDATE test
    start = time.time()
    for i in range(1, num_records + 1):
        enc_condition = f.encrypt('Updated Condition'.encode()).decode()
        cur.execute("""
            UPDATE patients_app_encryption 
            SET medical_condition = %s
            WHERE patient_id = %s
        """, (enc_condition, i))
    conn.commit()
    update_time = time.time() - start
    
    cur.close()
    conn.close()
    
    print(f"INSERT: {insert_time:.4f}s | SELECT: {select_time:.4f}s | UPDATE: {update_time:.4f}s")
    return {'insert': insert_time, 'select': select_time, 'update': update_time}

# Function to test performance of TDE
def test_tde(num_records):
    print(f"Testing TDE on WSL ({num_records} records)")
    
    try:
        conn = psycopg2.connect(**conn_params_wsl)
        cur = conn.cursor()
        
        # Load data
        patients = load_patient_data(limit=num_records)
        
        # Clear table
        cur.execute("TRUNCATE patients_tde RESTART IDENTITY CASCADE")
        conn.commit()
        
        # INSERT test 
        start = time.time()
        for p in patients:
            cur.execute("""
                INSERT INTO patients_tde 
                (patient_id, name, date_of_birth, identification_card_no,
                 medical_condition, prescription)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (p['patient_id'], p['name'], p['date_of_birth'],
                  p['identification_card_no'], p['medical_condition'], p['prescription']))
        conn.commit()
        insert_time = time.time() - start
        
        # SELECT test
        start = time.time()
        cur.execute("SELECT * FROM patients_tde")
        results = cur.fetchall()
        select_time = time.time() - start
        
        # UPDATE test
        start = time.time()
        for i in range(1, num_records + 1):
            cur.execute("UPDATE patients_tde SET medical_condition = 'Updated Condition' WHERE patient_id = %s", (i,))
        conn.commit()
        update_time = time.time() - start
        
        cur.close()
        conn.close()
        
        print(f"INSERT: {insert_time:.4f}s | SELECT: {select_time:.4f}s | UPDATE: {update_time:.4f}s")
        return {'insert': insert_time, 'select': select_time, 'update': update_time}
        
    except psycopg2.OperationalError as e:
        print(f"Error details: {e}")
        return None

# Function to measure storage overhead
def measure_storage():
    print("Measuring Storage Overhead")
    
    storage_data = []
    
    # Windows PostgreSQL tables
    conn_win = psycopg2.connect(**conn_params_windows)
    cur_win = conn_win.cursor()
    
    tables_windows = [
        ('patients', 'No Encryption'),
        ('patients_column_encryption', 'Column Encryption'),
        ('patients_app_encryption', 'Application Encryption')
    ]
    
    for table, method in tables_windows:
        cur_win.execute(f"""
            SELECT pg_total_relation_size('{table}') as bytes,
                   pg_size_pretty(pg_total_relation_size('{table}')) as size,
                   COUNT(*) FROM {table}, (SELECT 1) as dummy
        """)
        result = cur_win.fetchone()
        
        cur_win.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur_win.fetchone()[0]
        
        storage_data.append({
            'Method': method,
            'Size': result[1],
            'Bytes': result[0],
            'Records': count,
            'Bytes_Per_Record': result[0] / count if count > 0 else 0
        })
        print(f"{method}: {result[1]} ({count} records)")
    
    cur_win.close()
    conn_win.close()
    
    # WSL PostgreSQL TDE table 
    try:
        conn_wsl = psycopg2.connect(**conn_params_wsl)
        cur_wsl = conn_wsl.cursor()
        
        cur_wsl.execute("""
            SELECT pg_total_relation_size('patients_tde') as bytes,
                   pg_size_pretty(pg_total_relation_size('patients_tde')) as size
        """)
        result = cur_wsl.fetchone()
        
        cur_wsl.execute("SELECT COUNT(*) FROM patients_tde")
        count = cur_wsl.fetchone()[0]
        
        storage_data.append({
            'Method': 'TDE',
            'Size': result[1],
            'Bytes': result[0],
            'Records': count,
            'Bytes_Per_Record': result[0] / count if count > 0 else 0
        })
        print(f"TDE: {result[1]} ({count} records)")
        
        cur_wsl.close()
        conn_wsl.close()
    except:
        print("TDE: Could not connect to WSL PostgreSQL")
    
    # Calculate overhead
    baseline = next((item['Bytes'] for item in storage_data if item['Method'] == 'No Encryption'), 0)
    for item in storage_data:
        item['Overhead_%'] = ((item['Bytes'] - baseline) / baseline * 100) if baseline > 0 else 0
        print(f"  {item['Method']} overhead: {item['Overhead_%']:.2f}%")
    
    return storage_data

# Function to run all tests
def run_all_tests():
    print("Testing Database Encryption Technique Performance")
    
    # Store all results
    results = {
        'No Encryption': {},
        'Column Encryption': {},
        'Application Encryption': {},
        'TDE': {}
    }
    
    # Run tests for each size
    for size in TEST_SIZES:
        print(f"\nTESTING WITH {size} RECORDS\n")
        
        reset_session_state()
        results['No Encryption'][size] = test_no_encryption(size)
        reset_session_state()
        results['Column Encryption'][size] = test_column_encryption(size)
        reset_session_state()
        results['Application Encryption'][size] = test_app_encryption(size)
        reset_session_state()
        results['TDE'][size] = test_tde(size)
    
    # Measure storage
    storage_data = measure_storage()
    
    save_results_csv(results, storage_data)
    create_charts(results)

    print("\nGenerated CSV report and performance visualization")


# Function to save results to a CSV file
def save_results_csv(results, storage_data):
    # Performance results
    perf_data = []
    for method, sizes in results.items():
        for size, metrics in sizes.items():
            if metrics:
                perf_data.append({
                    'Method': method,
                    'Records': size,
                    'Insert_Time_s': metrics['insert'],
                    'Select_Time_s': metrics['select'],
                    'Update_Time_s': metrics['update'],
                    'Total_Time_s': metrics['insert'] + metrics['select'] + metrics['update']
                })
    
    df_perf = pd.DataFrame(perf_data)
    df_perf.to_csv('performance_results.csv', index=False)
    
    # Storage results
    df_storage = pd.DataFrame(storage_data)
    df_storage.to_csv('storage_results.csv', index=False)

# Function to create chart visualizations
def create_charts(results):
    operations = ['insert', 'select', 'update']
    titles = ['INSERT Performance', 'SELECT Performance', 'UPDATE Performance']
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # Individual operation charts
    for op, title in zip(operations, titles):
        plt.figure(figsize=(10, 6))
        
        for idx, (method, sizes) in enumerate(results.items()):
            x_vals = []
            y_vals = []
            for size in TEST_SIZES:
                if size in sizes and sizes[size]:
                    x_vals.append(size)
                    y_vals.append(sizes[size][op])
            
            if x_vals:
                plt.plot(x_vals, y_vals, marker='o', label=method, 
                        color=colors[idx], linewidth=2, markersize=8)
        
        plt.xlabel('Number of Records', fontsize=12)
        plt.ylabel('Time (seconds)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{op}_performance.png', dpi=300)
        plt.close()
    
    # Combined comparison chart
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (op, title) in enumerate(zip(operations, titles)):
        ax = axes[idx]
        
        for midx, (method, sizes) in enumerate(results.items()):
            x_vals = []
            y_vals = []
            for size in TEST_SIZES:
                if size in sizes and sizes[size]:
                    x_vals.append(size)
                    y_vals.append(sizes[size][op])
            
            if x_vals:
                ax.plot(x_vals, y_vals, marker='o', label=method, 
                       color=colors[midx], linewidth=2, markersize=6)
        
        ax.set_xlabel('Number of Records', fontsize=10)
        ax.set_ylabel('Time (seconds)', fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('performance_comparison.png', dpi=300)
    plt.close()

# Run Tests
if __name__ == "__main__":
    run_all_tests()
