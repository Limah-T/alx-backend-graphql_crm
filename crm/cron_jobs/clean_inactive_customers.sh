#!/bin/bash

# Navigate to project root (adjust if your manage.py is elsewhere)
cd "$(dirname "$0")/../.." || exit

# Run Django shell command to delete inactive customers
deleted_count=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max
from customers.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)

inactive_customers = Customer.objects.annotate(
    last_order=Max('order__order_date')
).filter(last_order__lt=cutoff_date) | Customer.objects.filter(order__isnull=True)

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")
cutoff_date = timezone.now() - timedelta(days=365)

inactive_customers = Customer.objects.annotate(
    last_order=Max('order__order_date')
).filter(last_order__lt=cutoff_date) | Customer.objects.filter(order__isnull=True)

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log result with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted \$deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt