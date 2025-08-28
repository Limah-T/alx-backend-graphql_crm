from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$',
            message="Phone number must be in format: '+1234567890' or '123-456-7890'"
        )]
    )
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} (${self.price})"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Calculate total amount before saving
        if not self.pk:  # Only on creation
            self.total_amount = sum(p.price for p in self.products.all())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order #{self.id} by {self.customer.name}"
