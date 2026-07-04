from .models import Cart, CartItem

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Merge session cart if it exists
        session_cart_id = request.session.get('cart_id')
        if session_cart_id:
            try:
                session_cart = Cart.objects.get(id=session_cart_id, user=None)
                for item in session_cart.items.all():
                    # Merge item into user's cart
                    user_item, item_created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        user_item.quantity += item.quantity
                        user_item.save()
                session_cart.delete()
                del request.session['cart_id']
            except Cart.DoesNotExist:
                pass
        return cart
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user=None)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
        return cart
