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
        
        EXTRA_USER_IDS = [
            '99e9e7d2-f0e6-4c7b-b86e-507e8aaa18f9', '876a0349-a5f6-4578-b5ec-2e1646dc83d9', 
            '8876fef6-c92e-43d2-a1a3-5b975f63b6da', '12669403-e478-4222-b8e5-b383b64c4e43', 
            '3e5451c5-e156-472f-8434-7af99f63e5c5', '42987414-5fd0-479a-8915-13b05fff8353', 
            'faec0961-c8e3-4fc0-a19f-668823708b12', '0eb3dad9-818e-45af-8962-73990313bd30', 
            '548249e9-6743-455d-b4e7-8b37f343ea1c', '3f2dd9ce-09b7-4b13-a0d2-3b0ef9a02484', 
            '10cc5afa-166c-4e59-b0d5-506947022cdb', '414acc48-a820-458b-ac25-f9113f487a01', 
            '5980781e-4e0d-4e39-93c5-ef15653de2ef', 'c8db46c1-4f11-45ff-b2bc-ab29b83e8009', 
            '53e749d6-dcab-4ed3-832b-ef459bbe1273', '5aa17db3-9d8f-4a04-8c6f-0d6fd440b2c4', 
            '33324b7d-44b9-4203-81fa-acfb1b29025e'
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
            OR
            uwc.user_id::varchar IN ({','.join([f"'{x}'" for x in EXTRA_USER_IDS])})
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

        print(f"Fetched {len(portal_users)} users from Database.")
        
        needs_update = True
        if os.path.exists(USERS_JSON_PATH):
            try:
                with open(USERS_JSON_PATH, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                old_keys = set([f"{u.get('userId', '')}_{u.get('roleCode', '')}_{u.get('jurisdictionId', '')}" for u in old_data])
                
                new_users = [u for u in portal_users if f"{u.get('userId', '')}_{u.get('roleCode', '')}_{u.get('jurisdictionId', '')}" not in old_keys]
                
                if new_users:
                    print(f"\n[NEW] You have {len(new_users)} NEW user assignments added to the portal:")
                    for nu in new_users:
                        print(f"      + {nu['firstName']} {nu['lastName']} -> {nu['designationCode']} ({nu['jurisdictionId']})")
                    print()
                elif len(portal_users) != len(old_data):
                    print(f"\n[INFO] User count changed from {len(old_data)} to {len(portal_users)}. Updating portal.\n")
                else:
                    print("\n[INFO] No new users or changes were found. Everything is already up-to-date!")
                    needs_update = False
            except Exception as ex:
                print(f"[WARN] Could not compare with old data: {ex}")

        if not needs_update:
            return
            
        print(f"Updating {USERS_JSON_PATH} and creating backup...")
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
