from carshop.models import Car


def order_saver(order, client, car, Order, OrderQuantity):
    if order:
        OrderQuantity.objects.create(
            car_type=car.car_type, quantity=1, order=order
        )

    else:
        order = Order.objects.create(client=client)
        OrderQuantity.objects.create(
            car_type=car.car_type, quantity=1, order=order
        )

    car.block(order)
    car.add_owner(client)


def cars_counter(car):
    cars_count = Car.objects.filter(
        color=car.color,
        year=car.year,
        car_type__name=car.car_type.name,
        car_type__brand=car.car_type.brand,
    ).count()
    return cars_count


def img_finder(order_quantity):
    return (
        order_quantity.car_type.image.url
        if order_quantity.car_type.image
        else None
    )


def reset_car(car):
    car.unblock()
    car.remove_owner()
