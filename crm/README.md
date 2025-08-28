# CRM Celery Report Setup

# Install Dependencies
pip install -r requirements.txt

# Run Migrations
python manage.py migrate

# Start Services
redis-server

# Start Celery Worker
celery -A crm worker -l info

# Start Celery Beat
celery -A crm beat -l info

# Verify to ckeck if reports are logged in
cat /tmp/crm_report_log.txt


---

# ✅ This will generate a **weekly CRM report every Monday at 6:00 AM** and log it into `/tmp/crm_report_log.txt`.  
