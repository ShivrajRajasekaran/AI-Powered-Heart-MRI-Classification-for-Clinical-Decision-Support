import ibm_db
from .config import DB2_credentials

def get_db_connection():
    """Establishes and returns a Db2 connection."""
    try:
        conn_str = f"DATABASE={DB2_credentials['database']};HOSTNAME={DB2_credentials['hostname']};PORT={DB2_credentials['port']};PROTOCOL=TCPIP;UID={DB2_credentials['user']};PWD={DB2_credentials['password']};SECURITY=SSL"
        conn = ibm_db.connect(conn_str, "", "")
        print("IBM Db2 connection successful.")
        return conn
    except Exception as e:
        print(f"Db2 connection failed. Error: {e}")
        return None

def validate_patient(patient_id):
    """Checks if a patient exists and returns their details as a dictionary."""
    conn = get_db_connection()
    if not conn: return None
    try:
        sql = "SELECT PATIENT_ID, PATIENT_NAME, PATIENT_EMAIL, MRI_IMAGE_URL, DIAGNOSIS, CONFIDENCE_SCORE, LAST_UPDATED FROM PATIENTS WHERE PATIENT_ID = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, patient_id)
        ibm_db.execute(stmt)
        
        result = ibm_db.fetch_assoc(stmt)
        ibm_db.close(conn)
        return result if result else None
    except Exception as e:
        print(f"Db2 validate_patient failed. Error: {e}")
        if conn: ibm_db.close(conn)
        return None

def update_patient_record(patient_id, image_url, diagnosis, confidence):
    """Updates a patient's record after an MRI analysis."""
    conn = get_db_connection()
    if not conn: return False
    try:
        sql = "UPDATE PATIENTS SET MRI_IMAGE_URL = ?, DIAGNOSIS = ?, CONFIDENCE_SCORE = ? WHERE PATIENT_ID = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, image_url)
        ibm_db.bind_param(stmt, 2, diagnosis)
        ibm_db.bind_param(stmt, 3, float(confidence))
        ibm_db.bind_param(stmt, 4, patient_id)
        
        ibm_db.execute(stmt)
        print(f"Successfully updated record for patient ID: {patient_id}")
        ibm_db.close(conn)
        return True
    except Exception as e:
        print(f"Db2 update_patient_record failed. Error: {e}")
        if conn: ibm_db.close(conn)
        return False

def get_all_patient_ids():
    """Retrieves a list of all patient IDs."""
    conn = get_db_connection()
    if not conn: return None
    try:
        sql = "SELECT PATIENT_ID FROM PATIENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        
        patient_ids = []
        result = ibm_db.fetch_tuple(stmt)
        while result:
            patient_ids.append(result[0])
            result = ibm_db.fetch_tuple(stmt)
            
        ibm_db.close(conn)
        return patient_ids
    except Exception as e:
        print(f"Db2 get_all_patient_ids failed. Error: {e}")
        if conn: ibm_db.close(conn)
        return None

def get_patient_count():
    """Gets the total number of patients in the database."""
    conn = get_db_connection()
    if not conn: return None
    try:
        sql = "SELECT COUNT(*) FROM PATIENTS"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        result = ibm_db.fetch_tuple(stmt)
        ibm_db.close(conn)
        return result[0] if result else 0
    except Exception as e:
        print(f"Db2 get_patient_count failed. Error: {e}")
        if conn: ibm_db.close(conn)
        return None

def get_count_by_diagnosis(diagnosis):
    """Counts patients with a specific diagnosis."""
    conn = get_db_connection()
    if not conn: return None
    try:
        sql = "SELECT COUNT(*) FROM PATIENTS WHERE DIAGNOSIS = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, diagnosis)
        ibm_db.execute(stmt)
        result = ibm_db.fetch_tuple(stmt)
        ibm_db.close(conn)
        return result[0] if result else 0
    except Exception as e:
        print(f"Db2 get_count_by_diagnosis failed. Error: {e}")
        if conn: ibm_db.close(conn)
        return None

