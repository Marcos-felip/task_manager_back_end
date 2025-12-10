from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=256)
    user_email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)


class CreateOrgMembershipSerializer(serializers.Serializer):
    organization_name = serializers.CharField(max_length=256)
    user_id = serializers.UUIDField()
    role = serializers.CharField(max_length=32, required=False, allow_blank=True, default="owner")