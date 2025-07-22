from django.contrib import admin
from .models import User,Guide,Tourist,Agency
# Register your models here.
admin.site.register(User)
admin.site.register(Guide)
admin.site.register(Tourist)
admin.site.register(Agency)