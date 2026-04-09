from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('username', 'email', 'first_name',
                    'last_name', 'get_roles', 'is_staff')
    list_filter = ('groups', 'is_staff', 'is_superuser', 'is_active')

    fieldsets = UserAdmin.fieldsets

    @admin.display(description='Roles')
    def get_roles(self, obj):
        return ', '.join(obj.roles) or '—'


admin.site.register(User, CustomUserAdmin)