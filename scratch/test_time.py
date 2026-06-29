import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'polideportivo.settings')
django.setup()

from django.utils import timezone
from datetime import date, datetime
import datetime as dt

now = timezone.now()
local_now = timezone.localtime(now)
print(f"Timezone: {timezone.get_current_timezone()}")
print(f"Now UTC: {now}")
print(f"Local now: {local_now}")
print(f"Local time: {local_now.time()}")
print(f"Local date: {local_now.date()}")

fecha_obj = date(2026, 6, 27)
hora_inicio = dt.time(17, 0)

is_past = False
if fecha_obj < local_now.date():
    is_past = True
elif fecha_obj == local_now.date() and hora_inicio < local_now.time():
    is_past = True

print(f"is_past for 17:00 on 2026-06-27: {is_past}")
