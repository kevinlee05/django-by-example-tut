from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order':order})


# Create your views here.
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'],
                                        price=item['price'], quantity=item['quantity'])
            # clear the cart
            cart.clear()
            # launch asynchronouse task
            order_created.delay(order.id) # set the order in the session
            request.session['order_id'] = order.id # redirect to the payment
            return redirect(reverse('payment:process'))
            # render(request, 'orders/order/created.html',{'order':order})

    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html',{'cart': cart, 'form': form})
