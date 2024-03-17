from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Wishlist
from products.models import Product
from django.contrib.auth.decorators import login_required


@login_required
def wishlist(request):
    """
    View for displaying the user's wishlist.

    The view retrieves all wishlist products associated with the currently logged-in user
    and renders them on the wishlist template.
    """
    wishlist_items = Wishlist.objects.filter(user=request.user)

    context = {
        'wishlist': wishlist_items
    }
    return render(request, 'wishlist/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """
    View for adding a product to the wishlist if it's not already present.
    """
    product = get_object_or_404(Product, pk=product_id)

    # Check if the product is already in the user's wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        messages.warning(
            request,
            f'{product.name} is already in your wishlist.')
        return redirect('product_detail', product_id=product_id)

    # Add the product to the wishlist using the correct product primary key
    Wishlist.objects.create(user=request.user, product_id=product_id)
    messages.success(request, f'{product.name} added to your wishlist.')
    return redirect('product_detail', product_id=product_id)


@login_required
def remove_from_wishlist(request, product_id):
    """
    View for removing a product from the wishlist if it exists.
    """
    product = get_object_or_404(Product, pk=product_id)

    # Check if the product is in the user's wishlist
    wishlist_item = Wishlist.objects.filter(
        user=request.user, product=product).first()
    if not wishlist_item:
        messages.warning(request, f'{product.name} is not in your wishlist.')
        return redirect('product_detail', product_id=product_id)

    # Remove the product from the wishlist
    wishlist_item.delete()
    messages.success(request, f'{product.name} removed from your wishlist.')
    return redirect('product_detail', product_id=product_id)
