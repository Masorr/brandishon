from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Wishlist
from products.models import Product


def wishlist(request):
    """
    View for displaying the user's wishlist.
    """
    wishlist_items = Wishlist.objects.filter(user=request.user)

    context = {
        'wishlist': wishlist_items
    }
    return render(request, 'wishlist/wishlist.html', context)