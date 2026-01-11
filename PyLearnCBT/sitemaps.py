from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ['PylearnCBT', 'features', 'contact',  'signup', 'about']

    def location(self, item):
        if item == 'about':
            return reverse('PylearnCBT') + '#about'
        elif item == 'contact':
            return reverse('PylearnCBT') + '#contact'
        elif item == 'features':
            return reverse('PylearnCBT') + '#features'
        elif item == 'signup':
            return reverse('PylearnCBT') + '#signup'
        return reverse(item)