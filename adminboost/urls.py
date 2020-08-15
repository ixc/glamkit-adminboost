
from django.contrib import admin

urlpatterns = list(getattr(admin.site, '_inline_urls', {}).values())
