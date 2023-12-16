from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required

from .models import User

admin.site.login = login_required(admin.site.login)
admin.site.site_header = "Proboj"
admin.site.site_title = "Proboj"

admin.site.register(User, UserAdmin)
