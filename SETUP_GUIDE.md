# Valora Beauty - Django Ecommerce Setup Guide

This is a complete multi-page luxury ecommerce website for Valora Beauty built with Django and Tailwind CSS.

## Project Structure

```
project/
├── templates/
│   ├── base.html              # Base template with header and footer
│   ├── home.html              # Home page with hero slider and bestsellers
│   ├── shop.html              # Shop page with product grid and filters
│   ├── collections.html       # Collections showcase page
│   ├── about.html             # About brand story page
│   └── contact.html           # Contact form and information
├── store/
│   ├── __init__.py
│   ├── views.py               # View functions for all pages
│   └── urls.py                # URL routing configuration
└── SETUP_GUIDE.md
```

## Installation & Setup

### 1. Create Django App

If you haven't already created the `store` app:

```bash
python manage.py startapp store
```

### 2. Update Project Settings

Add the `store` app to your Django `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',  # Add this line
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Ensure templates directory is included
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 3. Update Project URLs

Add the store app URLs to your project's main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),  # Add this line
]
```

### 4. Create Templates Directory

Make sure you have a `templates` directory in your project root:

```bash
mkdir templates
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000/` to see the website.

## Routes & Pages

| URL | View Function | Template | Description |
|-----|---------------|----------|-------------|
| `/` | `home` | `home.html` | Landing page with hero slider and bestsellers |
| `/shop/` | `shop` | `shop.html` | Product listing with filters (price, category, sort) |
| `/collections/` | `collections` | `collections.html` | Category showcase with seasonal collections |
| `/about/` | `about` | `about.html` | Brand story and company information |
| `/contact/` | `contact` | `contact.html` | Contact form and FAQ |

## Features

### Home Page
- Auto-rotating hero slider (changes every 5 seconds)
- Manual slider navigation with arrows
- Featured In section with luxury publication logos
- Shop by Collection cards
- Bestsellers product grid
- Newsletter subscription form

### Shop Page
- Responsive product grid (1, 2, 3 columns based on screen size)
- Price filter (Under $50, $50-$100, $100-$200, Over $200)
- Category filter (Skincare, Makeup, Fragrance, Accessories)
- Sort options (Newest, Price Low-High, Price High-Low, Best Sellers, Top Rated)
- Product cards with ratings and Add to Cart buttons
- Pagination controls

### Collections Page
- Three main category cards (Skincare, Makeup, Fragrance)
- Four seasonal collections (Spring, Summer, Autumn, Winter)
- Collection preview cards with hover effects
- Benefits highlights section

### About Page
- Brand mission, vision, and values
- Company statistics and achievements
- Team member profiles
- Newsletter signup

### Contact Page
- Contact form with validation
- Contact information (phone, email, address, hours)
- FAQ section with expandable items
- Map placeholder

## Design System

### Color Palette
- **Background**: `#fdf5f0` (Soft Nude)
- **Foreground**: `#222222` (Deep Charcoal)
- **Accent**: `#a67c52` (Golden Bronze)
- **Border**: `#e8dfd7` (Soft Gray)

### Typography
- **Headings**: Playfair Display (serif) - for elegant, high-end feel
- **Body**: Geist (sans-serif) - for clean, readable content

### Components
All styled using Tailwind CSS from CDN in `base.html`:

- `.btn-primary` - Main action button (dark with accent hover)
- `.btn-secondary` - Secondary button (bordered)
- `.input-field` - Form inputs with focus states
- `.nav-link` - Navigation links with underline hover effect
- `.product-card` - Product showcase with hover elevation
- `.section-title` - Large section headings

## Customization Guide

### Adding Products

Edit the `PRODUCTS` list in `store/views.py`:

```python
PRODUCTS = [
    {
        'id': 1,
        'name': 'Product Name',
        'description': 'Short description',
        'price': 99.00,
        'category': 'Skincare',  # or 'Makeup', 'Fragrance', etc.
        'rating': 5,  # 1-5
        'image': 'product-1.jpg',
    },
    # Add more products...
]
```

### Integrating with Database

Replace sample data with Django models:

```python
# store/models.py
from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('skincare', 'Skincare'),
        ('makeup', 'Makeup'),
        ('fragrance', 'Fragrance'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rating = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    newsletter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.name}"
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Adding Images

1. Configure static files in `settings.py`:
```python
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

2. Serve media files in `urls.py`:
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your urls
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

3. Update image references in templates:
```html
<img src="{{ product.image.url }}" alt="{{ product.name }}">
```

## Form Handling

The contact form includes:
- CSRF token protection
- Basic field validation
- Email field validation
- Success/error handling

### Saving Messages to Database

Update the `contact` view to save messages:

```python
from .models import ContactMessage

def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
            newsletter=bool(request.POST.get('newsletter')),
        )
        # ... rest of the code
```

## Active Link Highlighting

The navigation automatically highlights the current page using Django's `request.resolver_match.url_name`:

```html
<a href="{% url 'store:shop' %}" class="nav-link {% if request.resolver_match.url_name == 'shop' %}active{% endif %}">
    Shop
</a>
```

The `.nav-link.active` class in CSS shows the underline.

## Responsive Design

All pages are mobile-first responsive:
- Mobile: Single column layouts
- Tablet (md): 2-3 column grids
- Desktop (lg): Full multi-column layouts

Breakpoints used:
- `md:` - Medium screens (768px+)
- `lg:` - Large screens (1024px+)

## Performance Optimization

1. **Lazy Loading**: Add to images:
```html
<img src="..." loading="lazy" alt="...">
```

2. **Minified CSS**: Tailwind CDN automatically optimizes

3. **Static Files**: Configure Django's static file handling for production

4. **Caching**: Add view caching for frequently accessed pages:
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    # ...
```

## Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up static files collection: `python manage.py collectstatic`
- [ ] Configure media file serving
- [ ] Set up email backend for contact form
- [ ] Add SSL/HTTPS
- [ ] Configure database for production
- [ ] Set up environment variables
- [ ] Add security middleware and CSRF settings
- [ ] Test all forms and payment integration

## Support & Next Steps

1. **Add Payment Integration**: Stripe, PayPal, etc.
2. **User Accounts**: Registration, login, order history
3. **Shopping Cart**: Add to cart, checkout flow
4. **Search Functionality**: Search by name, category, price
5. **Reviews & Ratings**: Customer product reviews
6. **Wishlist**: Save favorite products
7. **Admin Dashboard**: Product management, order tracking
8. **Email Notifications**: Order confirmation, shipping updates

---

Built with Django, Tailwind CSS, and ❤️ for Valora Beauty
