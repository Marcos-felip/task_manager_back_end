from rest_framework import serializers
from accounts.infrastructure.models.user import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'username',
            'full_name',
            'org_active',
            'org_list'
        ]

    def get_full_name(self, obj: User) -> str:
        return getattr(obj, 'full_name', '')


class CreateUserMembershipInputSerializer(serializers.Serializer):
    user = serializers.DictField(child=serializers.CharField(), help_text="Dados do usuário (email, username, etc)")
    organization_id = serializers.UUIDField(help_text="ID da organização para vincular")
    membership = serializers.DictField(required=False, help_text="Dados de associação (ex: role)")

