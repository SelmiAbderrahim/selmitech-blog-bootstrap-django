from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post


class Static_Sitemap(Sitemap):

    priority = 1.0
    changefreq = 'daily'


    def items(self):
        return ['home', ]

    def location(self, item):
        return reverse(item)


class Post_Sitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Post.objects.all().filter(approved=True)

    def location(self, obj):
        return "/post/"+obj.slug

    def lastmod(self, obj): 
        return obj.date