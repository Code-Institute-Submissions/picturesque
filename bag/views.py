from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from products.models import Product


def view_bag(request):
    """ A view to return the shopping bag page """
    sizing = {
        'xs': 'XS - 4"x6"',
        's': 'S - 8"x10"',
        'm': 'M - 11"x14"',
        'l': 'L - 16"x20"',
        'xl': 'XL - 24"x36"',
        'xxl': 'XXL - 30"x40"',
    }

    context = {
        'sizes': sizing,
    }

    return render(request, 'bag/bag.html', context)


def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    if item_id in list(bag.keys()):
        if size in bag[item_id]['items_by_size'].keys():
            bag[item_id]['items_by_size'][size] += quantity
            messages.success(request, f'Updated quantity of {size.upper()}\
                {product.name} to {bag[item_id]["items_by_size"][size]}')
        else:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Added \
                                 {size.upper()} {product.name} to your bag')
    else:
        bag[item_id] = {'items_by_size': {size: quantity}}
        messages.success(request, f'Added \
            {size.upper()} {product.name} to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust the quantity of the specified product in the shopping bag """
    product = get_object_or_404(Product, pk=item_id)
    print('product: ', product)
    print('POST request: ', request.POST)
    quantity = int(request.POST.get('quantity'))
    size = request.POST['product_size']
    bag = request.session.get('bag', {})
    print(bag)

    if quantity > 0:
        bag[item_id]['items_by_size'][size] = quantity
        messages.success(request, f'Updated quantity of {size.upper()}\
                {product.name} to {bag[item_id]["items_by_size"][size]}')
    else:
        del bag[item_id]['items_by_size'][size]
        if not bag[item_id]['items_by_size']:
            bag.pop(item_id)
        messages.success(request, f'Removed {size.upper()}\
            {product.name} from your bag')

    request.session['bag'] = bag
    return redirect(reverse("view_bag"))


def remove_from_bag(request, item_id):
    """ Remove the specified product from the shopping bag """

    try:
        product = get_object_or_404(Product, pk=item_id)
        size = request.POST['product_size']
        bag = request.session.get('bag', {})
        print(bag[item_id]['items_by_size'][size])
        del bag[item_id]['items_by_size'][size]
        if not bag[item_id]['items_by_size']:
            bag.pop(item_id)
        messages.success(request, f'Removed {size.upper()}\
            {product.name} from your bag')

        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
