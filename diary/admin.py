from django.contrib import admin

from .models import *

# admin.site.register(Model)

admin.site.register(Account)
admin.site.register(Club)

admin.site.register(Action)
admin.site.register(Week)
admin.site.register(Activity)

admin.site.register(Change)
