from decimal import Decimal
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import Product, Order, OrderItem, Review, Wishlist, Category
from .forms import ProductForm, CheckoutForm, ReviewForm, UserRegistrationForm


def _get_cart(request):
    return request.session.setdefault('cart', {})


def _cart_item_count(request):
    return sum(_get_cart(request).values())


def _cart_items(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()
        if not product:
            continue
        line_total = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'line_total': line_total,
        })
        total += line_total
    return items, total


def home(request):
    query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    products = Product.objects.all()
    categories = Category.objects.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    products = products.order_by('-created_at')
    
    return render(request, 'index.html', {
        'products': products,
        'categories': categories,
        'search_query': query,
        'cart_count': _cart_item_count(request),
        'selected_category': category_id,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = product.reviews.all()
    user_review = None
    can_review = False
    
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        can_review = True
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': form.cleaned_data['rating'], 'comment': form.cleaned_data['comment']}
            )
            messages.success(request, 'Your review has been saved!')
            return redirect('product_detail', id=product.id)
    else:
        form = ReviewForm()
    
    return render(request, 'recipe_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_review': user_review,
        'can_review': can_review,
        'form': form,
        'cart_count': _cart_item_count(request),
    })


def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    if not product.is_in_stock():
        messages.error(request, 'This product is currently unavailable.')
        return redirect('product_detail', id=id)

    cart = _get_cart(request)
    cart[str(product.id)] = cart.get(str(product.id), 0) + 1
    request.session.modified = True
    messages.success(request, f'Added {product.name} to your cart.')
    return redirect('cart_detail')


def cart_detail(request):
    items, total = _cart_items(request)
    return render(request, 'cart.html', {
        'items': items,
        'total': total,
        'cart_count': _cart_item_count(request),
    })


def remove_from_cart(request, id):
    cart = _get_cart(request)
    cart.pop(str(id), None)
    request.session.modified = True
    return redirect('cart_detail')


def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, 'You must be logged in to checkout.')
        return redirect('login')
    
    items, total = _cart_items(request)
    if not items:
        messages.info(request, 'Your cart is empty. Add products before checking out.')
        return redirect('home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                shipping_address=form.cleaned_data['shipping_address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                total_amount=total,
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price,
                )
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order_confirmation', id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'items': items,
        'total': total,
        'cart_count': _cart_item_count(request),
    })


def order_confirmation(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'order_confirmation.html', {
        'order': order,
        'cart_count': _cart_item_count(request),
    })


@login_required(login_url='login')
def add_product(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to add products.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('product_detail', id=product.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    return render(request, 'add_recipe.html', {
        'form': form,
        'title': 'Add Product',
        'cart_count': _cart_item_count(request),
    })


@login_required(login_url='login')
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit products.')
        return redirect('product_detail', id=id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_detail', id=product.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'edit_recipe.html', {
        'form': form,
        'product': product,
        'title': 'Edit Product',
        'cart_count': _cart_item_count(request),
    })


@login_required(login_url='login')
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete products.')
        return redirect('product_detail', id=id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('home')
    
    return render(request, 'delete_confirm.html', {
        'product': product,
        'title': 'Delete Product',
        'cart_count': _cart_item_count(request),
    })


# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create wishlist for new user
            Wishlist.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# Wishlist Views
@login_required(login_url='login')
def wishlist(request):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    return render(request, 'wishlist.html', {
        'wishlist': wishlist,
        'cart_count': _cart_item_count(request),
    })


@login_required(login_url='login')
@require_http_methods(["POST"])
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if product in wishlist.products.all():
        messages.info(request, f'{product.name} is already in your wishlist.')
    else:
        wishlist.products.add(product)
        messages.success(request, f'{product.name} added to your wishlist!')
    
    return redirect('product_detail', id=id)


@login_required(login_url='login')
@require_http_methods(["POST"])
def remove_from_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist.products.remove(product)
    messages.success(request, f'{product.name} removed from your wishlist.')
    
    return redirect('wishlist')


# User Dashboard/Orders
@login_required(login_url='login')
def user_orders(request):
    orders = request.user.orders.all()
    return render(request, 'user_orders.html', {
        'orders': orders,
        'cart_count': _cart_item_count(request),
    })