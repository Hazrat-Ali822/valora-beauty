from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ecommerce.views import admin_dashboard
urlpatterns = [
    path('admin/', admin.site.urls),
    # Use the imported function directly:
    path('dashboard/', admin_dashboard, name='admin_dashboard'), 
    path('', include('ecommerce.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)