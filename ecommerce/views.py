import json
import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Review, Order, OrderItem, WishlistItem, ContactMessage, SliderImage
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta


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
    # 1. Base query: Sirf stock wale products
    products = Product.objects.filter(stock__gt=0)
    
    # 2. Get parameters from URL
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '')
    price_range = request.GET.get('price')
    sort_option = request.GET.get('sort')

    # 3. Apply Filters
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Price Filter Logic
    if price_range:
        if price_range == '0-2000':
            products = products.filter(price__lt=2000)
        elif price_range == '2000-5000':
            products = products.filter(price__gte=2000, price__lte=5000)
        elif price_range == '5000-10000':
            products = products.filter(price__gte=5000, price__lte=10000)
        elif price_range == '10000+':
            products = products.filter(price__gt=10000)

    # 4. Sorting Logic
    if sort_option == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_option == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at') # Yakeeni banayein model mein created_at hai

    context = {
        'products': products,
        'total_products': products.count(),
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
    # Seasonal items dictionary
    seasonal_items = [
        {'name': 'Spring', 'color': 'from-yellow-400 to-green-400'},
        {'name': 'Summer', 'color': 'from-orange-400 to-yellow-300'},
        {'name': 'Autumn', 'color': 'from-red-500 to-orange-400'},
        {'name': 'Winter', 'color': 'from-blue-500 to-cyan-400'},
        {'name': 'New Year', 'color': 'from-pink-500 to-red-400'},
        {'name': 'Trending', 'color': 'from-purple-500 to-violet-400'},
    ]
    return render(request, 'collections.html', {
        'categories': categories, 
        'seasonal_items': seasonal_items
    })

# ─── SEARCH ──────────────────────────────────────────────────────────────────
def search(request):
    query = request.GET.get('q', '')
    is_ajax = request.GET.get('ajax') == 'true'
    
    # Product filter logic
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Agar request AJAX hai, to sirf JSON data bhejein
    if is_ajax:
        results = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': float(p.price), # Price ko float mein convert karein
                'category': p.category.name if p.category else "No Category"
            } for p in products
        ]
        return JsonResponse({'status': 'success', 'products': results})

    # Agar normal request hai, to page render karein
    return render(request, 'search.html', {'results': products, 'query': query})


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
    # 'wishlist_items' variable bhejna zaroori hai
    items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': items})

# Toggle Wishlist View
def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Login required'})
    if request.method == 'POST':
        data = json.loads(request.body)
        product = get_object_or_404(Product, pk=data.get('product_id'))
        obj, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            obj.delete()
            return JsonResponse({'success': True, 'added': False})
        return JsonResponse({'success': True, 'added': True})
    return JsonResponse({'success': False})

# ─── AUTH ─────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
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
                if user.is_staff:
                    return redirect('admin_dashboard')
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




def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ─── ADMIN DASHBOARD (main view) ─────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_dashboard(request):
    now = timezone.now()
    today_start  = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start   = now - timedelta(days=7)
    month_start  = now - timedelta(days=30)

    # ── KPI Stats ──────────────────────────────────────────
    total_revenue = Order.objects.filter(
        status='delivered'
    ).aggregate(t=Sum('total_price'))['t'] or 0

    total_orders    = Order.objects.count()
    total_products  = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    pending_orders_count = Order.objects.filter(status='pending').count()

    today_sales  = Order.objects.filter(created_at__gte=today_start,  status='delivered').aggregate(t=Sum('total_price'))['t'] or 0
    week_sales   = Order.objects.filter(created_at__gte=week_start,   status='delivered').aggregate(t=Sum('total_price'))['t'] or 0
    month_sales  = Order.objects.filter(created_at__gte=month_start,  status='delivered').aggregate(t=Sum('total_price'))['t'] or 0
    avg_order_value = Order.objects.aggregate(a=Avg('total_price'))['a'] or 0

    # ── Products ───────────────────────────────────────────
    all_products      = Product.objects.select_related('category').all()
    top_products      = all_products.order_by('-stock')[:10]
    low_stock_products = all_products.filter(stock__gt=0, stock__lt=10).order_by('stock')[:5]

    in_stock_count     = all_products.filter(stock__gt=10).count()
    low_stock_count    = all_products.filter(stock__gt=0, stock__lte=10).count()
    out_of_stock_count = all_products.filter(stock=0).count()

    # ── Orders ─────────────────────────────────────────────
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    all_orders    = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    # ── Customers ──────────────────────────────────────────
    all_customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('order'),
        total_spent=Sum('order__total_price'),
    ).order_by('-date_joined')

    # ── Categories ─────────────────────────────────────────
    categories = Category.objects.annotate(product_count=Count('products')).all()

    # ── Analytics ──────────────────────────────────────────
    order_status_stats = Order.objects.values('status').annotate(count=Count('id'))

   
    top_categories = list(Category.objects.annotate(
        sales=Sum('products__orderitem__price')
    ).order_by('-sales')[:5])
    total_cat_sales = sum(c.sales or 0 for c in top_categories)
    for cat in top_categories:
        cat.percentage = round((cat.sales or 0) / total_cat_sales * 100) if total_cat_sales else 0
        cat.total_sales = cat.sales or 0

    context = {
        'total_revenue':        f'{total_revenue:,.0f}',
        'total_orders':         total_orders,
        'total_products':       total_products,
        'total_customers':      total_customers,
        'pending_orders_count': pending_orders_count,

        'today_sales':      f'{today_sales:,.0f}',
        'week_sales':       f'{week_sales:,.0f}',
        'month_sales':      f'{month_sales:,.0f}',
        'avg_order_value':  f'{avg_order_value:,.0f}',

        'all_products':        all_products,
        'top_products':        top_products,
        'low_stock_products':  low_stock_products,
        'in_stock_count':      in_stock_count,
        'low_stock_count':     low_stock_count,
        'out_of_stock_count':  out_of_stock_count,

        'recent_orders':       recent_orders,
        'all_orders':          all_orders,
        'all_customers':       all_customers,

        'categories':          categories,
        'order_status_stats':  order_status_stats,
        'top_categories':      top_categories,
    }
    return render(request, 'admin_dashboard.html', context)


# ─── ORDER: STATUS UPDATE (AJAX) ─────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_order_status(request, order_id):
    try:
        data   = json.loads(request.body)
        status = data.get('status', '')
        valid  = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if status not in valid:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save()
        return JsonResponse({'success': True, 'status': order.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── ORDER: DETAIL HTML (AJAX modal) ────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        id=order_id
    )

    # Shipping address — Order model may store these directly
    shipping = {
        'name':    getattr(order, 'full_name', order.user.get_full_name() or order.user.username),
        'phone':   getattr(order, 'phone', '—'),
        'address': getattr(order, 'address', '—'),
        'city':    getattr(order, 'city', '—'),
        'email':   getattr(order, 'email', order.user.email),
    }

    rows_html = ''
    for item in order.items.all():
        line_total = item.price * item.quantity
        rows_html += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #F3F4F6;">{item.product.name}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #F3F4F6;text-align:right;">{item.quantity}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #F3F4F6;text-align:right;">PKR {item.price:,.0f}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #F3F4F6;text-align:right;font-weight:600;">PKR {line_total:,.0f}</td>
        </tr>"""

    status_colors = {
        'pending': '#92400E', 'processing': '#1E40AF',
        'shipped': '#5B21B6', 'delivered': '#065F46', 'cancelled': '#991B1B',
    }
    status_bgs = {
        'pending': '#FEF3C7', 'processing': '#DBEAFE',
        'shipped': '#EDE9FE', 'delivered': '#D1FAE5', 'cancelled': '#FEE2E2',
    }
    sc = status_colors.get(order.status, '#374151')
    sb = status_bgs.get(order.status, '#F3F4F6')

    html = f"""
    <div style="font-size:13px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
        <div style="background:#F9FAFB;border-radius:8px;padding:14px;">
          <p style="color:#6B7280;font-size:10px;font-weight:700;text-transform:uppercase;margin-bottom:8px;letter-spacing:.5px;">Customer</p>
          <p style="font-weight:700;font-size:14px;margin-bottom:2px;">{shipping['name']}</p>
          <p style="color:#6B7280;">{shipping['email']}</p>
          <p style="color:#6B7280;margin-top:4px;">📞 {shipping['phone']}</p>
        </div>
        <div style="background:#F9FAFB;border-radius:8px;padding:14px;">
          <p style="color:#6B7280;font-size:10px;font-weight:700;text-transform:uppercase;margin-bottom:8px;letter-spacing:.5px;">Delivery</p>
          <p style="font-weight:600;">📍 {shipping['address']}</p>
          <p style="color:#6B7280;">{shipping['city']}</p>
          <p style="margin-top:6px;">
            <span style="background:{sb};color:{sc};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;text-transform:capitalize;">
              {order.status}
            </span>
          </p>
        </div>
      </div>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#F9FAFB;">
            <th style="padding:8px 12px;text-align:left;font-size:10px;font-weight:700;text-transform:uppercase;color:#6B7280;border-bottom:1px solid #E5E7EB;">Product</th>
            <th style="padding:8px 12px;text-align:right;font-size:10px;font-weight:700;text-transform:uppercase;color:#6B7280;border-bottom:1px solid #E5E7EB;">Qty</th>
            <th style="padding:8px 12px;text-align:right;font-size:10px;font-weight:700;text-transform:uppercase;color:#6B7280;border-bottom:1px solid #E5E7EB;">Unit Price</th>
            <th style="padding:8px 12px;text-align:right;font-size:10px;font-weight:700;text-transform:uppercase;color:#6B7280;border-bottom:1px solid #E5E7EB;">Total</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
      <div style="text-align:right;padding:16px 12px 0;border-top:2px solid #E5E7EB;margin-top:8px;">
        <span style="font-size:13px;color:#6B7280;">Order Total &nbsp;</span>
        <span style="font-size:20px;font-weight:700;color:#1F2937;">PKR {order.total_price:,.0f}</span>
      </div>
    </div>"""
    return HttpResponse(html)


# ─── PRODUCT: JSON for edit-form prefill (AJAX) ───────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_product_json(request, product_id):
    p = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'id':          p.id,
        'name':        p.name,
        'brand':       getattr(p, 'brand', ''),
        'description': p.description,
        'price':       str(p.price),
        'sale_price':  str(getattr(p, 'sale_price', '') or ''),
        'stock':       p.stock,
        'category_id': p.category_id,
        'sku':         getattr(p, 'sku', ''),
        'is_available': p.is_available,
        'is_featured': getattr(p, 'is_featured', False),
    })


# ─── PRODUCT: ADD ─────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_add_product(request):
    from django.utils.text import slugify
    try:
        cat = get_object_or_404(Category, id=request.POST.get('category'))
        name = request.POST.get('name', '').strip()

        # Generate unique slug
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = Product(
            name=name,
            slug=slug,
            description=request.POST.get('description', ''),
            price=float(request.POST.get('price', 0)),
            stock=int(request.POST.get('stock', 0)),
            category=cat,
            is_available='is_available' in request.POST,
        )
        # Optional fields (if they exist on your model)
        if hasattr(product, 'brand'):
            product.brand = request.POST.get('brand', '')
        if hasattr(product, 'sale_price') and request.POST.get('sale_price'):
            product.sale_price = float(request.POST.get('sale_price'))
        if hasattr(product, 'sku'):
            product.sku = request.POST.get('sku', '')
        if hasattr(product, 'is_featured'):
            product.is_featured = 'is_featured' in request.POST
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, f'Product "{name}" added successfully!')
    except Exception as e:
        messages.error(request, f'Error adding product: {e}')
    return redirect('store:admin_dashboard')


# ─── PRODUCT: EDIT ────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cat = get_object_or_404(Category, id=request.POST.get('category'))
        product.name        = request.POST.get('name', product.name)
        product.description = request.POST.get('description', '')
        product.price       = float(request.POST.get('price', product.price))
        product.stock       = int(request.POST.get('stock', product.stock))
        product.category    = cat
        product.is_available = 'is_available' in request.POST

        if hasattr(product, 'brand'):
            product.brand = request.POST.get('brand', '')
        if hasattr(product, 'sale_price') and request.POST.get('sale_price'):
            product.sale_price = float(request.POST.get('sale_price'))
        if hasattr(product, 'sku'):
            product.sku = request.POST.get('sku', '')
        if hasattr(product, 'is_featured'):
            product.is_featured = 'is_featured' in request.POST
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, f'Product "{product.name}" updated!')
    except Exception as e:
        messages.error(request, f'Error updating product: {e}')
    return redirect('store:admin_dashboard')


# ─── PRODUCT: DELETE (AJAX) ───────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_delete_product(request, product_id):
    try:
        get_object_or_404(Product, id=product_id).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── PRODUCT: TOGGLE FEATURED (AJAX) ─────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_toggle_featured(request, product_id):
    try:
        data    = json.loads(request.body)
        product = get_object_or_404(Product, id=product_id)
        if hasattr(product, 'is_featured'):
            product.is_featured = data.get('featured', False)
            product.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── PRODUCT: UPDATE STOCK (AJAX) ─────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_update_stock(request, product_id):
    try:
        data    = json.loads(request.body)
        product = get_object_or_404(Product, id=product_id)
        product.stock = max(0, int(data.get('stock', 0)))
        product.save()
        return JsonResponse({'success': True, 'stock': product.stock})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── CATEGORY: ADD ────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_add_category(request):
    from django.utils.text import slugify
    name = request.POST.get('name', '').strip()
    if name:
        Category.objects.get_or_create(
            name=name,
            defaults={
                'slug': slugify(name),
                'description': request.POST.get('description', ''),
            }
        )
        messages.success(request, f'Category "{name}" added!')
    return redirect('store:admin_dashboard')


# ─── CATEGORY: DELETE (AJAX) ──────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_delete_category(request, cat_id):
    try:
        get_object_or_404(Category, id=cat_id).delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── CSV IMPORT (AJAX) ────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
@require_POST
def admin_csv_import(request):
    from django.utils.text import slugify
    try:
        rows = json.loads(request.body).get('products', [])
        if not rows:
            return JsonResponse({'success': False, 'error': 'No data in CSV'})

        imported, errors = 0, []
        for row in rows:
            try:
                name = row.get('name', '').strip()
                if not name:
                    continue

                cat_name = row.get('category', 'General').strip()
                cat, _ = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'slug': slugify(cat_name)}
                )

                # Build slug
                base_slug = slugify(name)
                slug, n = base_slug, 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{n}"; n += 1

                defaults = {
                    'slug':         slug,
                    'description':  row.get('description', ''),
                    'price':        float(row.get('price', 0) or 0),
                    'stock':        int(row.get('stock', 0) or 0),
                    'category':     cat,
                    'is_available': True,
                }
                # Optional fields
                p, created = Product.objects.get_or_create(name=name, defaults=defaults)
                if not created:
                    # Update existing
                    for k, v in defaults.items():
                        if k != 'slug':
                            setattr(p, k, v)
                    p.save()

                if hasattr(p, 'brand'):
                    p.brand = row.get('brand', ''); p.save()
                if hasattr(p, 'sku'):
                    p.sku = row.get('sku', ''); p.save()

                imported += 1
            except Exception as e:
                errors.append(f"Row '{row.get('name','')}': {e}")

        return JsonResponse({'success': True, 'imported': imported, 'errors': errors[:5]})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ─── EXPORT CSV ───────────────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_export_csv(request):
    export_type = request.GET.get('type', 'products')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="valora_{export_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
    )
    writer = csv.writer(response)

    if export_type == 'orders':
        writer.writerow(['Order ID', 'Customer', 'Email', 'Phone', 'City', 'Total (PKR)', 'Status', 'Date'])
        for o in Order.objects.select_related('user').all():
            writer.writerow([
                o.id,
                getattr(o, 'full_name', o.user.username),
                getattr(o, 'email', o.user.email),
                getattr(o, 'phone', ''),
                getattr(o, 'city', ''),
                o.total_price,
                o.status,
                o.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

    elif export_type == 'customers':
        writer.writerow(['ID', 'Username', 'Email', 'Joined', 'Orders', 'Total Spent (PKR)'])
        for u in User.objects.filter(is_staff=False).annotate(
            order_count=Count('order'),
            total_spent=Sum('order__total_price')
        ):
            writer.writerow([
                u.id, u.username, u.email,
                u.date_joined.strftime('%Y-%m-%d'),
                u.order_count or 0, u.total_spent or 0,
            ])

    else:  # products
        writer.writerow(['ID', 'Name', 'Brand', 'Category', 'Price', 'Sale Price', 'Stock', 'SKU', 'Available'])
        for p in Product.objects.select_related('category').all():
            writer.writerow([
                p.id, p.name,
                getattr(p, 'brand', ''),
                p.category.name if p.category else '',
                p.price,
                getattr(p, 'sale_price', ''),
                p.stock,
                getattr(p, 'sku', ''),
                p.is_available,
            ])

    return response