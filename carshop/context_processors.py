from .models import Order, Car


def cart_items_count(request):
    if request.user.is_authenticated:
        client = request.user
        order = Order.objects.filter(client_id=client, is_paid=False).first()
        if order:
            cart_count = Car.objects.filter(blocked_by_order=order).count()
            return {"cart_items_count": cart_count}
    return {"cart_items_count": 0}
