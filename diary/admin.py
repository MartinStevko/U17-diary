from django.contrib import admin

from .models import *

# admin.site.register(Model)

admin.site.register(Account)
admin.site.register(OldPoints)
admin.site.register(Club)
admin.site.register(Code)

admin.site.register(Action)
admin.site.register(Week)
admin.site.register(Activity)
admin.site.register(Message)

admin.site.register(EvaulationChanges)
admin.site.register(DuplicateError)
