from django.contrib import admin

from .models import User, Organization, Membership


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = (
     "email",
     "username",
     "org_ativa",
     "is_staff",
     "is_superuser",
    )
	search_fields = (
     "email",
     "username",
    )
	list_filter = (
     "is_staff",
     "is_superuser",
    )

	def org_ativa(self, obj: User):
		if not obj.org_active_id:
			return "—"
		org = Organization.objects.filter(organization_id=obj.org_active_id).first()
		return org.name if org else "—"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	list_display = (
      "name",
      "email",
      "cpf",
      "is_active",
     )
	search_fields = (
      "name",
      "email",
      "cpf",
     )
	list_filter = ("is_active",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = (
     "user_email",
     "organization_name",
     "role",
     "is_active",
     "created_at",
    )
	search_fields = (
     "role",
    )
	list_filter = (
     "role",
     "is_active",
    )

	def user_email(self, obj: Membership):
		user = User.objects.filter(user_id=obj.user_id).first()
		return user.email if user else "—"

	def organization_name(self, obj: Membership):
		org = Organization.objects.filter(organization_id=obj.organization_id).first()
		return org.name if org else "—"
