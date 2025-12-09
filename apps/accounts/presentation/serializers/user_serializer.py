from rest_framework import serializers
from accounts.infrastructure.models.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'username',
            'org_active',
            'org_list'
        ]


class CreateUserMembershipInputSerializer(serializers.Serializer):
    user = serializers.DictField(child=serializers.CharField(), help_text="Dados do usuário (email, username, etc)")
    organization_id = serializers.UUIDField(help_text="ID da organização para vincular")
    membership = serializers.DictField(required=False, help_text="Dados de associação (ex: role)")

