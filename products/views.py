from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm
from checkout.models import OrderLineItem

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
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
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

    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if request.user.is_authenticated:
                # Check if the user has bought the product
                has_bought_product = OrderLineItem.objects.filter(order__user_profile__user=request.user, product=product).exists()
                if has_bought_product:
                    # Check if the user has already reviewed this product
                    if product.reviews.filter(author=request.user).exists():
                        messages.error(request, 'You have already reviewed this product.')
                    else:
                        # Save the review
                        review = review_form.save(commit=False)
                        review.author = request.user
                        review.product = product
                        review.save()
                        messages.success(request, 'Review submitted successfully!')
                        return redirect('product_detail', product_id=product_id)
                else:
                    messages.error(request, 'You need to buy this product to review it.')
            else:
                messages.error(request, 'You need to log in to review this product.')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')

    # Render product detail page with the review form and reviews
    context = {
        'product': product,
        'reviews': reviews,
        'review_count': review_count,
        'review_form': review_form,
    }
    return render(request, 'products/product_detail.html', context)


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
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
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
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
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