from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Organization, Membership

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        full_name = validated_data['full_name']
        email = validated_data['email']
        password = validated_data['password']

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=email
        )

        return user


class OrganizationSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Organization
        fields = [
            'name',
            'email', 
            'organization_id',
            'user_id'
        ]

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado com a chave fornecida.")
        
        organization = Organization.objects.create(**validated_data)
        
        Membership.objects.create(
            user=user,
            organization=organization,
            role=Membership.Roles.OWNER,
            is_active=True
        )
        
        user.org_active = organization
        user.save()
        
        return organization


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['user'] = {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'org_active': {
                'name': self.user.org_active.name if self.user.org_active else None,
                'organization_key': self.user.org_active.key if self.user.org_active else None
            }
        }
        
        return data