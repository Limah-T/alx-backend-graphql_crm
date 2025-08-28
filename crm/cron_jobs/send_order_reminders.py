#!/usr/bin/env python3
import sys
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def main():
    try:
        # Setup GraphQL transport
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Define date range (last 7 days)
        today = datetime.utcnow().date()
        cutoff_date = today - timedelta(days=7)

        # GraphQL query
        query = gql(
            """
            query GetRecentOrders($cutoff: Date!) {
                orders(orderDate_Gte: $cutoff) {
                    id
                    customer {
                        email
                    }
                }
            }
            """
        )

        params = {"cutoff": str(cutoff_date)}
        result = client.execute(query, variable_values=params)

        # Process results
        orders = result.get("orders", [])
        for order in orders:
            order_id = order["id"]
            customer_email = order["customer"]["email"]
            logging.info(f"Order ID: {order_id}, Customer Email: {customer_email}")

        print("Order reminders processed!")

    except Exception as e:
        logging.error(f"Error processing order reminders: {e}")
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
