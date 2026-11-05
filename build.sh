
#!/usr/bin/env bash
set -o errexit

# ติดตั้ง Python Packages
pip install -r requirements.txt

# รวบรวม Static Files
python manage.py collectstatic --noinput

# สร้างหรืออัปเดตตารางฐานข้อมูล
python manage.py migrate
