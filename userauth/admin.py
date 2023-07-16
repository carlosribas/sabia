from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ['pk', 'email', 'username', 'first_name', 'last_name']
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': ('email', 'first_name', 'last_name', 'academic_background', 'other', 'certificate', 'phone', 'cpf')
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('academic_background', 'other', 'certificate', 'phone', 'cpf')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
