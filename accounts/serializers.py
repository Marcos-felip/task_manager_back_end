from rest_framework import serializers
from django.contrib.auth import get_user_model
from auth.models import Membership, Organization
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer para a gestão de membros da organização"""
    
    role = serializers.ChoiceField(
        choices=Membership.Roles.choices, 
        default=Membership.Roles.MEMBER,
        required=False
    )
    
    password = serializers.CharField(write_only=True, required=True)
    
    full_name = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    status = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'status',
            'password'
        ]
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        if self.instance is None and 'password' in attrs:
            try:
                validate_password(attrs['password'])
            except ValidationError as e:
                raise serializers.ValidationError({'password': e.messages})
        
        return attrs

    def validate_email(self, value):
        if self.instance is None or (self.instance and self.instance.email != value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Um usuário com este email já existe.")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', Membership.Roles.MEMBER)
        password = validated_data.pop('password')
        full_name = validated_data.pop('full_name')
        
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        organization = self.context.get('organization')
        if not organization:
            raise serializers.ValidationError("Organização não encontrada no contexto.")
        
        user = User.objects.create_user(
            username=validated_data['email'],
            password=password,
            first_name=first_name,
            last_name=last_name,
            **validated_data
        )
        
        membership = Membership.objects.create(
            user=user,
            organization=organization,
            role=role,
            is_active=True
        )
        
        if not user.org_active:
            user.org_active = organization
            user.save()
        
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        
        validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        organization = self.context.get('organization')
        
        if organization and role is not None:
            try:
                membership = Membership.objects.get(user=instance, organization=organization)
                membership.role = role
                membership.save()
            except Membership.DoesNotExist:
                pass
        
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        data.pop('full_name', None)
        data.pop('password', None)
        
        organization = self.context.get('organization')
        
        if not organization and hasattr(instance, 'org_active'):
            organization = instance.org_active
            
        if organization:
            try:
                membership = Membership.objects.get(user=instance, organization=organization)
                data['role'] = membership.get_role_display()
                data['status'] = membership.is_active
            except Membership.DoesNotExist:
                data['role'] = None
                data['status'] = False
        
        return data