import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Review, Order, OrderItem, WishlistItem, ContactMessage, SliderImage


# ─── HOME ───────────────────────────────────────────────────────────────────
def home(request):
    products = Product.objects.filter(stock__gt=0)[:8]
    categories = Category.objects.all()
    sliders = {s.slide_type: s for s in SliderImage.objects.filter(is_active=True)}
    
    # Category images from slider
    category_images = {
        'skincare': sliders.get('cerave'),
        'makeup': sliders.get('makeup'),
        'fragrance': sliders.get('fragrance'),
    }
    
    featured_brands = ['CeraVe', 'The Ordinary', 'Lattafa', 'Miss Rose', 'Maybelline', 'Rasasi', 'Afnan', 'Body n Body']
    fragrance_brands = ['Lattafa', 'Rasasi', 'Afnan', 'Armaf', 'Oud Elite']
    
    context = {
        'products': products,
        'categories': categories,
        'featured_brands': featured_brands,
        'fragrance_brands': fragrance_brands,
        'sliders': sliders,
        'category_images': category_images,
    }
    return render(request, 'home.html', context)



# ─── SHOP ────────────────────────────────────────────────────────────────────
def shop(request):
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'shop.html', context)


# ─── PRODUCT DETAIL ──────────────────────────────────────────────────────────
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')
    related = Product.objects.filter(category=product.category).exclude(slug=slug)[:4]
    context = {
        'product': product,
        'reviews': reviews,
        'related': related,
    }
    return render(request, 'product_detail.html', context)


# ─── COLLECTIONS ─────────────────────────────────────────────────────────────
def collections(request):
    categories = Category.objects.all()
    return render(request, 'collections.html', {'categories': categories})


# ─── SEARCH ──────────────────────────────────────────────────────────────────
def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'search.html', {'results': results, 'query': query})


# ─── CART (session based) ─────────────────────────────────────────────────────
def cart(request):
    cart_data = request.session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, item in cart_data.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
        })
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))

        product = get_object_or_404(Product, pk=product_id)
        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
            }

        request.session['cart'] = cart
        total_items = sum(i['quantity'] for i in cart.values())
        return JsonResponse({'success': True, 'total_items': total_items})
    return JsonResponse({'success': False})


def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        cart = request.session.get('cart', {})
        cart.pop(product_id, None)
        request.session['cart'] = cart
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        cart = request.session.get('cart', {})
        if product_id in cart:
            if quantity <= 0:
                cart.pop(product_id)
            else:
                cart[product_id]['quantity'] = quantity
        request.session['cart'] = cart
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# ─── CHECKOUT ─────────────────────────────────────────────────────────────────
def checkout(request):
    cart_data = request.session.get('cart', {})
    if not cart_data:
        return redirect('store:cart')

    cart_items = []
    total = 0
    for product_id, item in cart_data.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        cart_items.append({**item, 'id': product_id, 'subtotal': subtotal})

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            total_price=total,
        )
        for product_id, item in cart_data.items():
            try:
                product = Product.objects.get(pk=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price'],
                )
            except Product.DoesNotExist:
                pass

        request.session['cart'] = {}
        messages.success(request, f'Order #{order.id} placed successfully! We will contact you soon.')
        return redirect('store:home')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})


# ─── WISHLIST ─────────────────────────────────────────────────────────────────
@login_required
def wishlist(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': items})


def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Login required'})
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        obj, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            obj.delete()
            return JsonResponse({'success': True, 'added': False})
        return JsonResponse({'success': True, 'added': True})
    return JsonResponse({'success': False})


# ─── AUTH ─────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                return redirect('store:home')
            else:
                error = 'Invalid password.'
        except User.DoesNotExist:
            error = 'No account found with this email.'
    return render(request, 'login.html', {'error': error})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(email=email).exists():
            error = 'An account with this email already exists.'
        else:
            username = email.split('@')[0]
            base = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            )
            login(request, user)
            return redirect('store:home')
    return render(request, 'signup.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('store:home')


# ─── PROFILE ─────────────────────────────────────────────────────────────────
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('store:profile')
    return render(request, 'profile.html', {'orders': orders})


# ─── ABOUT & CONTACT ──────────────────────────────────────────────────────────
def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject', 'General Inquiry'),
            message=request.POST.get('message'),
        )
        messages.success(request, 'Your message has been sent! We will get back to you soon.')
        return redirect('store:contact')
    return render(request, 'contact.html')
