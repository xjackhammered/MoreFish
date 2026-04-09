from django.db import models
from django.contrib.sessions.models import Session
from core.models import CoreModel

# Create your models here.
class Cart(CoreModel):
    user = models.ForeignKey('users.User',blank=True, null=True,on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session,blank=True, null=True,on_delete=models.DO_NOTHING)
    
    @property
    def total_price(self):
        # Calculate total price from cart items
        total = 0
        for cart_item in self.cartitem_set.all():
            total += cart_item.price
        return total
    
    def __str__(self) -> str:
        return self.user.first_name

class CartItem(CoreModel):
    cart = models.ForeignKey('cart.Cart',blank=True, null=True,on_delete=models.DO_NOTHING)
    product = models.ForeignKey("product.Product",blank=True, null=True, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.product.name