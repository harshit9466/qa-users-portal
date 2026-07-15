@echo off
echo ==============================================
echo Installing required Python packages...
pip install psycopg2-binary -q
echo ==============================================
echo Running Database Sync...
python sync_users.py
echo ==============================================
pause
