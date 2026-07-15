import os
import sys

# Windows double-click safe: set correct working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        import json
        import subprocess
        import datetime
        import shutil
        
        try:
            import psycopg2
        except ImportError:
            print("[INFO] 'psycopg2-binary' is missing. Auto-installing it for your Python environment...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
            print("[SUCCESS] Installation successful. Continuing sync...\n")
            import psycopg2

        # ==========================================
        # CONFIGURATION
        # ==========================================
        DB_HOST = "10.10.8.158" 
        DB_PORT = "5432"
        DB_NAME = "biharone_dev" 
        DB_USER = "postgres" 
        DB_PASS = "postgres" 
        
        USERS_JSON_PATH = "users.json"
        # ==========================================
        
        VALID_DISTRICT_BLOCK_IDS = [
            '1', '3', '400', '401', '402', '464', '465', '466', '467',
            '1585', '1586', '1587', '1588', '1589', '1590', '1591', '1592', '1593', '1594', '1595', '1596', '1597', '1598', '1599', '1600', '1601', '1602', '1603',
            '1960', '1961', '1962', '1963', '1964', '1965', '1966', '1967', '1968', '1969', '1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979', '1980', '1981', '1982'
        ]
        
        VALID_PS_IDS = [
            '549', '550', '551', '552', '553', '554', '555', '556', '557', '558', '561', '562', '563', '564', '565', '566', '567', '568', '569', '570', '571', '572', '574', '575', '576', '579', '580', '582', '584', '586', '588', '589', '590', '592', '593', '594', '597', '581', '577', '573', '559', '595', '578', '591', '596', '587', '585', '583', '560', '852', '851', '853', '854', '855', '863', '856', '859', '857', '860', '861', '858', '872', '869', '873', '871', '874', '864', '865', '866', '862', '870', '867', '868', '877', '878', '875', '876'
        ]
        
        QUERY = f"""
        SELECT 
            uwc.user_id, uwc.department_id, uwc.role_code, 
            uwc.jurisdiction_type, uwc.jurisdiction_id,
            u.first_name, u.last_name, u.email
        FROM public.user_workload_capacity uwc
        JOIN iam_service.users u ON uwc.user_id::varchar = u.id::varchar
        WHERE (
            (uwc.jurisdiction_type IN ('DISTRICT', 'SUB_DISTRICT', 'BLOCK') AND uwc.jurisdiction_id IN ({','.join([f"'{x}'" for x in VALID_DISTRICT_BLOCK_IDS])}))
            OR
            (uwc.jurisdiction_type = 'POLICE_STATION' AND uwc.jurisdiction_id IN ({','.join([f"'{x}'" for x in VALID_PS_IDS])}))
        )
        """
        
        print("Connecting to database...")
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        print("Running query to fetch valid users...")
        cur.execute(QUERY)
        rows = cur.fetchall()
        
        portal_users = []
        for row in rows:
            uid, dept_id, role, jur_type, jur_id, fname, lname, email = row
            desig = role.replace("_ROLE", "")
            if desig.endswith("_HOME"): desig = desig.replace("_HOME", "")

            portal_users.append({
                "employeeId": "", "firstName": fname, "middleName": "",
                "lastName": lname if lname else "", "email": email, "mobile": "9999999999",
                "roleCode": role, "jurisdictionType": jur_type, "jurisdictionId": jur_id,
                "designationCode": desig, "userId": uid, "departmentId": dept_id
            })
            
        cur.close()
        conn.close()

        print(f"Fetched {len(portal_users)} users. Updating {USERS_JSON_PATH}...")
        
        if os.path.exists(USERS_JSON_PATH):
            backup_dir = "previous_versions"
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"users_{timestamp}.json")
            shutil.copy2(USERS_JSON_PATH, backup_file)
            print(f"Backed up old users.json to {backup_file}")
            
        with open(USERS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(portal_users, f, indent=2)

        print("Committing and pushing to GitHub...")
        subprocess.run(["git", "add", USERS_JSON_PATH], check=True)
        if os.path.exists("previous_versions"):
            subprocess.run(["git", "add", "previous_versions/"], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-sync users from DB and backup old version"], check=False)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("\nSUCCESS: Sync Complete! Website will update in 1-2 minutes.")

    except Exception as e:
        import traceback
        print("\n================== ERROR OCCURRED ==================")
        traceback.print_exc()
        print("====================================================")
        print("Please check your DB credentials, VPN connection, or Git setup.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
