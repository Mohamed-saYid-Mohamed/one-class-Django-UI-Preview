def cart_icon(request):
    from .utils import get_cart
    if request.path.startswith('/admin/'):
        return {}
    try:
        cart = get_cart(request)
        return {'cart': cart}
    except Exception:
        return {}
