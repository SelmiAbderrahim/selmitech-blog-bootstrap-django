
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from filebrowser.sites import site
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

from django.contrib.sitemaps.views import sitemap
from pages.sitemaps import Static_Sitemap
from pages.sitemaps import Post_Sitemap

sitemaps = {
    'article': Post_Sitemap(),
    'static': Static_Sitemap(),
}

urlpatterns = [
    path('sasuke/', admin.site.urls),
    path('', include("pages.urls")),
    path('hitcount/', include('hitcount.urls', namespace='hitcount')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('grappelli/', include('grappelli.urls')),
    path('ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)