import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from django.db import transaction
from crm.models import Customer, Order
from crm.models import Product
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.core.validators import validate_email
from django.utils import timezone
from django.db.models import Sum
import re


# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Error Types
class ErrorType(graphene.ObjectType):
    field = graphene.String()
    messages = graphene.List(graphene.String)

class MutationResult(graphene.Union):
    class Meta:
        types = (CustomerType, ProductType, OrderType, ErrorType)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    errors = graphene.Field(ErrorType)
    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input):
        try:
            # Validate phone format if provided
            if input.phone:
                phone_regex = r'^\+?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$'
                if not re.match(phone_regex, input.phone):
                    raise ValidationError("Phone number must be in format: '+1234567890' or '123-456-7890'")
            
            # Validate email format
            validate_email(input.email)
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone or ""
            )
            customer.full_clean()
            customer.save()
            
            return CreateCustomer(customer=customer, success=True)
            
        except ValidationError as e:
            return CreateCustomer(
                errors=ErrorType(
                    field=list(e.message_dict.keys())[0], 
                    messages=list(e.message_dict.values())[0],
                    success=False
                )
            )

        except IntegrityError:
            return CreateCustomer(
                errors=ErrorType(field="email", messages=["Email already exists"]),
                success=False
            )
        except Exception as e:
            return CreateCustomer(
                errors=ErrorType(field="non_field_errors", messages=[str(e)]),
                success=False
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()

    @staticmethod
    @transaction.atomic
    def mutate(root, info, inputs):
        customers = []
        errors = []
        success = True
        
        for idx, input in enumerate(inputs):
            try:
                # Validate phone format if provided
                if input.phone:
                    phone_regex = r'^\+?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$'
                    if not re.match(phone_regex, input.phone):
                        raise ValidationError("Invalid phone format")
                
                validate_email(input.email)
                
                customer = Customer(
                    name=input.name,
                    email=input.email,
                    phone=input.phone or ""
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
                
            except Exception as e:
                error_field = "email" if "email" in str(e).lower() else "phone" if "phone" in str(e).lower() else "row"
                error_msg = str(e)
                if isinstance(e, ValidationError):
                    error_msg = list(e.message_dict.values())[0][0]
                
                errors.append(
                    ErrorType(
                        field=f"{error_field} (row {idx+1})",
                        messages=[error_msg]
                    )
                )
                success = False
        
        return BulkCreateCustomers(
            customers=customers,
            errors=errors,
            success=success
        )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.Field(ErrorType)
    success = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input):
        try:
            if float(input.price) <= 0:
                raise ValidationError("Price must be positive")
            
            if input.stock and int(input.stock) < 0:
                raise ValidationError("Stock cannot be negative")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            
            return CreateProduct(product=product, success=True)
            
        except Exception as e:
            return CreateProduct(
                errors=ErrorType(
                    field="price" if "price" in str(e).lower() else "stock" if "stock" in str(e).lower() else "non_field_errors",
                    messages=[str(e)]
                ),
                success=False
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.Field(ErrorType)
    success = graphene.Boolean()

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError("Customer does not exist")
            
            # Validate products exist and get them
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    raise ValidationError(f"Product with ID {product_id} does not exist")
            
            if not products:
                raise ValidationError("At least one product must be specified")
            
            # Create order
            order = Order.objects.create(customer=customer)
            order.products.set(products)
            order.save()  # Triggers total_amount calculation
            
            return CreateOrder(order=order, success=True)
            
        except Exception as e:
            return CreateOrder(
                errors=ErrorType(
                    field="customer_id" if "customer" in str(e).lower() else "product_ids" if "product" in str(e).lower() else "non_field_errors",
                    messages=[str(e)]
                ),
                success=False
            )

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    customer = graphene.relay.Node.Field(CustomerNode)
    all_customers = DjangoFilterConnectionField(CustomerNode)

    products = graphene.List(ProductType)
    product = graphene.relay.Node.Field(ProductNode)
    all_products = DjangoFilterConnectionField(ProductNode)

    orders = graphene.List(OrderType)
    order = graphene.relay.Node.Field(OrderNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.select_related('customer').prefetch_related('products').all()
    
    def resolve_all_customers(self, info, **kwargs):
        return CustomerFilter(kwargs).qs

    def resolve_all_products(self, info, **kwargs):
        return ProductFilter(kwargs).qs

    def resolve_all_orders(self, info, **kwargs):
        return OrderFilter(kwargs).qs

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments needed

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += 10  # simulate restock
            product.save()
            updated_products.append(product)

        return UpdateLowStockProducts(
            updated_products=updated_products,
            message=f"Updated {len(updated_products)} low-stock products at {timezone.now()}",
        )


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()

    def resolve_total_customers(root, info):
        return Customer.objects.count()

    def resolve_total_orders(root, info):
        return Order.objects.count()

    def resolve_total_revenue(root, info):
        return Order.objects.aggregate(total=Sum("totalamount"))["total"] or 0.0
