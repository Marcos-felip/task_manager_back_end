from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class CreateOrgMembershipSerializer(serializers.Serializer):
    organization_name = serializers.CharField()
    organization_email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    cpf_cnpj = serializers.CharField()
    user_id = serializers.UUIDField()
    role = serializers.CharField(required=False, allow_blank=True)