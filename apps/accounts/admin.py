from django.contrib import admin

from .models import User, Organization, Membership


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = (
     "email",
     "username",
     "org_active",
     "is_staff",
     "is_superuser"
    )
	search_fields = (
     "email",
     "username"
    )
	list_filter = (
     "is_staff",
     "is_superuser",
     "org_active"
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	list_display = (
     "name",
     "email",
     "cpf_cnpj",
     "is_active"
    )
	search_fields = (
     "name",
     "email",
     "cpf_cnpj"
    )
	list_filter = ("is_active",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = (
     "user",
     "organization",
     "role",
     "is_active",
     "created"
    )
	search_fields = (
     "user__email",
     "user__username",
     "organization__name"
    )
	list_filter = (
     "role",
     "is_active"
    )
