from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from account.models import User
from cart.models import Order, ProductsInOrder
from catalog.models import Product
import logging

logger = logging.getLogger(__name__)


def add_to_cart(request):
    path = request.GET.get('next')

    if request.method == 'POST':
        product_id = request.GET.get('product_id')

        if 'cart' not in request.session:
            request.session['cart'] = {}

        cart = request.session.get('cart')

        if product_id in cart:
            cart[product_id]['quantity'] += 1

        else:
            cart[product_id] = {
                'quantity': 1
            }

    request.session.modified = True
    return redirect(path)


def view_cart(request):
    path = request.GET.get('next')

    context = {
        'next': path,
    }

    cart = request.session.get('cart', None)

    if cart:
        products = {}
        product_list = Product.objects.filter(pk__in=cart.keys()).values('id', 'title', 'description')

        for product in product_list:
            products[str(product['id'])] = product

        for key in cart.keys():
            cart[key]['product'] = products[key]

        context['cart'] = cart

    return render(request, 'cart/cart.html', context)


@login_required(login_url='login')
def view_order(request):
    if request.method == 'POST':
        user_id = request.user.pk
        customer = User.objects.get(pk=user_id)

        cart = request.session['cart']

        if len(cart) > 0:
            order = Order.objects.create(customer=customer)

            for key, value in cart.items():
                product = Product.objects.get(pk=key)
                quantity = value['quantity']
                ProductsInOrder.objects.create(order=order, product=product, quantity=quantity)

            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, 'Заказ принят')

    return redirect('cart:cart')

@login_required(login_url='login')
def view_orders(request):
    user_id = request.user.pk
    customer = User.objects.get(pk=user_id)
    orders = Order.objects.filter(customer=customer)
    logger.info(orders)
    context = {
        'orders': orders
    }
    return render(request, 'cart/orders.html', context)
