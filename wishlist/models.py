from django.db import models
from django.contrib.auth.models import User
from products.models import Product

# Create your models here.


class Wishlist(models.Model):
    '''
    Stores wishlist related to a :model:`Product` made by :model:`auth.User`
    '''
    product = models.ForeignKey(
        Product,
        related_name="wishlist_items",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name="wishlist",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.username}'s Wishlist Item: {self.product.name}"
