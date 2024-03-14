from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone

from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm
from checkout.models import OrderLineItem
from wishlist.models import Wishlist

# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(
                name__icontains=query) | Q(
                description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """
    A view to display individual product details and reviews and provide
    functionality for users who've bought product to submit a review.

    It returns a rendered product detail page with product information,
    existing reviews, and a form to submit new reviews.

    A user can only submit a review once of a product.

    has_bought_product checks if user has made an order that contains
    a product which matches the product they like to review,
    indicating they've bought the product.
    """

    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.all().order_by("-created_on")
    review_count = product.reviews.count()
    review_form = ReviewForm()
    wishlist_product_ids = Wishlist.objects.filter(
        user=request.user).values_list(
        'product_id', flat=True)

    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if request.user.is_authenticated:
                # Check if the user has bought the product
                has_bought_product = OrderLineItem.objects.filter(
                    order__user_profile__user=request.user, product=product).exists()
                if has_bought_product:
                    # Check if the user has already reviewed this product
                    if product.reviews.filter(author=request.user).exists():
                        messages.error(
                            request, 'You have already reviewed this product.')
                    else:
                        # Save the review
                        review = review_form.save(commit=False)
                        review.author = request.user
                        review.product = product
                        review.save()
                        messages.success(
                            request, 'Review submitted successfully!')
                        return redirect(
                            'product_detail', product_id=product_id)
                else:
                    messages.error(
                        request, 'You need to buy this product to review it.')
            else:
                messages.error(
                    request, 'You need to log in to review this product.')
        else:
            messages.error(
                request, 'Invalid form submission. Please try again.')

    # Check if the user has an existing review for this product
    user_has_review = False
    if request.user.is_authenticated:
        user_has_review = product.reviews.filter(author=request.user).exists()

    # Render product detail page with the review form, reviews and wishlist
    # button
    context = {
        'product': product,
        'reviews': reviews,
        'review_count': review_count,
        'review_form': review_form,
        'user_has_review': user_has_review,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def edit_review(request, review_id):
    """
    Edit a review

    Updates created_on date if editing of review is saved
    """
    review = get_object_or_404(Review, pk=review_id)
    if request.user == review.author:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                review.created_on = timezone.now()
                form.save()
                messages.success(request, 'Review updated successfully!')
                return redirect('product_detail', product_id=review.product.id)
            else:
                messages.error(
                    request, 'Failed to update review. Please ensure the form is valid.')
        else:
            form = ReviewForm(instance=review)
            messages.info(request, 'You are editing your review.')

        context = {
            'form': form,
            'review': review,
        }
        return render(request, context)
    else:
        messages.error(request, 'You are not authorized to edit this review.')
        return redirect('product_detail', product_id=review.product.id)


@login_required
def delete_review(request, review_id):
    """ Delete a review """
    review = get_object_or_404(Review, pk=review_id)
    if request.user == review.author:
        product_id = review.product.id
        review.delete()
        messages.success(request, 'Review deleted!')
        # Redirect back to the product detail page to refresh page
        return redirect('product_detail', product_id=product_id)
    else:
        messages.error(request, 'Only the author of the review can delete it.')
        return redirect('product_detail', product_id=review.product.id)


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
