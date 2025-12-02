from django.contrib import admin
from .models import User, Organization, Membership

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'org_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'organization_id', 'is_active')
    search_fields = ('name', 'email', 'organization_id')
    list_filter = ('is_active',)
    ordering = ('name',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active', 'created', 'updated')
    search_fields = ('user__email', 'organization__name')
    list_filter = ('role', 'is_active')
    ordering = ('-created',)
