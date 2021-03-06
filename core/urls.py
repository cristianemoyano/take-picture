from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'', include('snapshot.urls', namespace='snapshot')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
