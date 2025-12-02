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
    is_member_active = serializers.BooleanField(required=False, default=True)
    membership_created = serializers.DateTimeField(read_only=True)
    
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
            'created',
            'role',
            'is_member_active', 
            'membership_created',
            'password',
            'password_confirm'
        ]
        read_only_fields = ['id', 'created', 'membership_created']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email

    def validate(self, attrs):
        if self.instance is None and 'password' in attrs:
            if not attrs.get('password_confirm'):
                raise serializers.ValidationError("Confirmação de senha é obrigatória.")
            
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("As senhas não coincidem.")
            
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
        is_member_active = validated_data.pop('is_member_active', True)
        password_confirm = validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        organization = self.context.get('organization')
        if organization:
            membership = Membership.objects.create(
                user=user,
                organization=organization,
                role=role,
                is_active=is_member_active
            )
            
            user.membership_created = membership.created
            
            if not user.org_active:
                user.org_active = organization
                user.save()
        
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        is_member_active = validated_data.pop('is_member_active', None)
        
        validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        organization = self.context.get('organization')
        if organization and (role is not None or is_member_active is not None):
            try:
                membership = Membership.objects.get(user=instance, organization=organization)
                if role is not None:
                    membership.role = role
                if is_member_active is not None:
                    membership.is_active = is_member_active
                membership.save()
            except Membership.DoesNotExist:
                pass
        
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        organization = self.context.get('organization')
        if organization:
            try:
                membership = Membership.objects.get(user=instance, organization=organization)
                data['role'] = membership.role
                data['is_member_active'] = membership.is_active
                data['membership_created'] = membership.created
            except Membership.DoesNotExist:
                data['role'] = None
                data['is_member_active'] = None
                data['membership_created'] = None
        
        return data