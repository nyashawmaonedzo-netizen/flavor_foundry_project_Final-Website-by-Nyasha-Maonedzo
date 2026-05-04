from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Product, Order, OrderItem
from .forms import ProductForm, CheckoutForm


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
    products = Product.objects.order_by('-created_at')
    return render(request, 'index.html', {
        'products': products,
        'cart_count': _cart_item_count(request),
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'recipe_detail.html', {
        'product': product,
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
    items, total = _cart_items(request)
    if not items:
        messages.info(request, 'Your cart is empty. Add products before checking out.')
        return redirect('home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
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


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_recipe.html', {
        'form': form,
        'page_title': 'Add a New Product',
    })


def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_recipe.html', {
        'form': form,
        'product': product,
        'page_title': 'Edit Product',
    })


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        return redirect('home')
    return render(request, 'delete_confirm.html', {
        'product': product,
        'cart_count': _cart_item_count(request),
    })