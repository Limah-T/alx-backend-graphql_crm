import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """Log CRM heartbeat and optionally check GraphQL endpoint."""
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Always log heartbeat
    with open(LOG_FILE, "a") as f:
        f.write(f"{now} CRM is alive\n")

    try:
        # Optional: verify GraphQL endpoint
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=1,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("{ hello }")
        response = client.execute(query)

        with open(LOG_FILE, "a") as f:
            f.write(f"{now} GraphQL hello response: {response.get('hello')}\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{now} GraphQL check failed: {e}\n")

LOG_FILE = "/tmp/low_stock_updates_log.txt"

def update_low_stock():
    """Call GraphQL mutation to update low-stock products and log results."""
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=1,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        mutation = gql("""
            mutation {
              updateLowStockProducts {
                message
                updatedProducts {
                  id
                  name
                  stock
                }
              }
            }
        """)

        response = client.execute(mutation)
        result = response["updateLowStockProducts"]

        with open(LOG_FILE, "a") as f:
            f.write(f"{now} - {result['message']}\n")
            for p in result["updatedProducts"]:
                f.write(f"   Updated {p['name']} → New stock: {p['stock']}\n")

    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{now} - Failed to update low stock: {e}\n")