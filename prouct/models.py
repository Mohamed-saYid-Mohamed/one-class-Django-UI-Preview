from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    description = models.TextField(null=True)
    image_url = models.JSONField(blank=True, default=list)

    class Meta:
        db_table = 'prouct_products'

    def __str__(self):
        return self.name

# Backward compatibility alias
products = Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    city = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.total_price:
            if self.product:
                self.total_price = Decimal(str(self.product.price)) * self.quantity
            else:
                self.total_price = Decimal('0.00')
        super().save(*args, **kwargs)
        
        # If product is present (direct order), create corresponding OrderItem if it doesn't exist
        if self.product:
            OrderItem.objects.get_or_create(
                order=self,
                product=self.product,
                defaults={
                    'quantity': self.quantity,
                    'price': Decimal(str(self.product.price))
                }
            )

    def __str__(self):
        if self.product:
            return f'Order #{self.id} - {self.full_name} - {self.product.name}'
        return f'Order #{self.id} - {self.full_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order #{self.order.id}'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        if self.user:
            return f'Cart of {self.user.username}'
        return f'Guest Cart #{self.id}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return Decimal(str(self.product.price)) * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Cart #{self.cart.id}'