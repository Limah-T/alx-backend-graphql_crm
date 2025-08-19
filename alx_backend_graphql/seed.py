import os
import django
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql.settings')
django.setup()

from crm.models import Customer, Product, Order

fake = Faker()

def seed_customers(count=10):
    for _ in range(count):
        Customer.objects.create(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number()[:15]
        )

def seed_products(count=5):
    for i in range(count):
        Product.objects.create(
            name=f"Product {i+1}",
            price=fake.random_number(digits=2),
            stock=fake.random_number(digits=2)
        )

def seed_orders(count=3):
    customers = Customer.objects.all()
    products = list(Product.objects.all())
    
    for _ in range(count):
        customer = fake.random_element(customers)
        order = Order.objects.create(customer=customer)
        order.products.set(fake.random_elements(products, length=2, unique=True))
        order.save()

if __name__ == '__main__':
    print("Seeding data...")
    seed_customers()
    seed_products()
    seed_orders()
    print("Seeding complete!")