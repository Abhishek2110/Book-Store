from django.db import models
from user.models import User
from book.models import Books

# Create your models here.
class Cart(models.Model):
    total_price = models.IntegerField(default=0)
    total_quantity = models.IntegerField(default=0)
    is_ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    class Meta:
        db_table = 'cart'
        
class CartItems(models.Model):
    price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    book = models.ForeignKey(Books, on_delete = models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    
    class Meta:
        db_table = 'cart_items'