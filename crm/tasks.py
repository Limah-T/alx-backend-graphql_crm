import requests
from datetime import datetime
from celery import shared_task

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

@shared_task
def generate_crm_report():
    query = """
    query {
      totalCustomers
      totalOrders
      totalRevenue
    }
    """
    response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
    data = response.json().get("data", {})

    customers = data.get("totalCustomers", 0)
    orders = data.get("totalOrders", 0)
    revenue = data.get("totalRevenue", 0.0)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

    with open("/tmp/crm_report_log.txt", "a") as log_file:
        log_file.write(log_entry)

    return log_entry
