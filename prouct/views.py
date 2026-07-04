from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal

from prouct.forms import OrderForm, CheckoutForm, RegisterForm
from prouct.models import Order, Product, OrderItem, Cart, CartItem
from prouct.utils import get_cart

# Keep existing products model name reference active in view logic
products = Product

def index(request):
    products_list = Product.objects.all()

    for product in products_list:
        image_data = product.image_url
        if isinstance(image_data, list) and image_data:
            product.display_image = image_data[0]
        elif isinstance(image_data, str) and image_data.strip():
            product.display_image = image_data.strip()
        else:
            product.display_image = "https://via.placeholder.com/150"

    return render(request, 'index.html', {
        "products": products_list,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    image_data = product.image_url
    if isinstance(image_data, list) and image_data:
        product.display_image = image_data[0]
    elif isinstance(image_data, str) and image_data.strip():
        product.display_image = image_data.strip()
    else:
        product.display_image = 'https://via.placeholder.com/900x700?text=Product+Image'

    if request.method == 'POST':
        # Protect direct orders with login requirement
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to place an order.')
            return redirect('login')
            
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.user = request.user
            if order.quantity > product.stock:
                form.add_error('quantity', f'Only {product.stock} items are available in stock.')
            else:
                with transaction.atomic():
                    order.save()
                    product.stock -= order.quantity
                    product.save(update_fields=['stock'])
                messages.success(request, 'Your order has been placed successfully.')
                return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm(initial={'quantity': 1})

    return render(request, 'product_detail.html', {
        'product': product,
        'form': form,
    })


def order_success(request, order_id):
    # Retrieve order based on user context if they are logged in, or get it directly for backwards compatibility
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})


# --- Authentication Views ---

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('index')


# --- Cart Views (AJAX) ---

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, product_id=product_id)
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Quantity must be positive.'})
        if quantity > product.stock:
            return JsonResponse({'success': False, 'message': f'Only {product.stock} items are in stock.'})
            
        cart = get_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cart_item.quantity + quantity > product.stock:
                return JsonResponse({'success': False, 'message': f'Cannot add. Total in cart ({cart_item.quantity + quantity}) exceeds stock ({product.stock}).'})
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'"{product.name}" added to cart.',
            'total_items': cart.total_items
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def update_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        cart = get_cart(request)
        if cart_item.cart != cart:
            return JsonResponse({'success': False, 'message': 'Permission denied.'})
            
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Quantity must be positive.'})
        if quantity > cart_item.product.stock:
            return JsonResponse({'success': False, 'message': f'Only {cart_item.product.stock} items in stock.'})
            
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'item_total': float(cart_item.total_price),
            'cart_total': float(cart.total_price),
            'total_items': cart.total_items,
            'message': 'Cart updated.'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        cart = get_cart(request)
        if cart_item.cart != cart:
            return JsonResponse({'success': False, 'message': 'Permission denied.'})
            
        cart_item.delete()
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.total_price),
            'total_items': cart.total_items,
            'message': 'Item removed.'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


def cart_detail(request):
    cart = get_cart(request)
    return render(request, 'cart.html', {'cart': cart})


# --- Checkout & Order Dashboard Views ---

@login_required
def checkout(request):
    cart = get_cart(request)
    if cart.items.count() == 0:
        messages.warning(request, 'Your cart is empty. Add products to checkout.')
        return redirect('index')
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Validate stock
            stock_valid = True
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    form.add_error(None, f'Insufficient stock for "{item.product.name}". Only {item.product.stock} available.')
                    stock_valid = False
                    
            if stock_valid:
                try:
                    with transaction.atomic():
                        order = Order.objects.create(
                            user=request.user,
                            full_name=form.cleaned_data['full_name'],
                            email=request.user.email or "noemail@example.com",
                            phone=form.cleaned_data['phone'],
                            address=form.cleaned_data['address'],
                            city=form.cleaned_data['city'],
                            notes=form.cleaned_data['notes'],
                            total_price=cart.total_price,
                            status='Pending'
                        )
                        for item in cart.items.all():
                            OrderItem.objects.create(
                                order=order,
                                product=item.product,
                                quantity=item.quantity,
                                price=Decimal(str(item.product.price))
                            )
                            # Decrement stock
                            item.product.stock -= item.quantity
                            item.product.save(update_fields=['stock'])
                        
                        # Clear cart
                        cart.items.all().delete()
                        
                    messages.success(request, 'Your order has been placed successfully!')
                    return redirect('order_success', order_id=order.id)
                except Exception as e:
                    form.add_error(None, f'An error occurred: {str(e)}')
    else:
        # Prepopulate using user information
        full_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        form = CheckoutForm(initial={
            'full_name': full_name,
            'email': request.user.email
        })
        
    return render(request, 'checkout.html', {
        'form': form,
        'cart': cart
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def view_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Pending':
        with transaction.atomic():
            order.status = 'Cancelled'
            order.save(update_fields=['status'])
            # Return stock
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        messages.success(request, f'Order #{order.id} has been cancelled successfully. Stock was returned.')
    else:
        messages.error(request, f'Order #{order.id} cannot be cancelled because its status is {order.status}.')
    return redirect('my_orders')


@login_required
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_cart(request)
    
    # Add items back to cart
    for item in order.items.all():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
        if not created:
            cart_item.quantity += item.quantity
        else:
            cart_item.quantity = item.quantity
        cart_item.save()
        
    messages.success(request, f'All items from Order #{order.id} have been added to your cart.')
    return redirect('cart_detail')




