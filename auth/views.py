from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, OrganizationSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class RegisterView(APIView):
    """
        Cadastre um novo usuário.
    """
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'full_name': {
                        'type': 'string',
                        'description': 'Nome completo do usuário',
                        'example': 'João Silva'
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'Endereço de email (será usado como nome de usuário)',
                        'example': 'joao.silva@email.com'
                    },
                    'password': {
                        'type': 'string',
                        'format': 'password',
                        'description': 'Senha para a conta',
                        'example': 'securepassword123'
                    }
                },
                'required': ['full_name', 'email', 'password']
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Usuário registrado com sucesso'
                    },
                    'user_key': {
                        'type': 'string',
                        'description': 'Chave única do usuário para criação de organização',
                        'example': 'ABC123DEF456'
                    }
                }
            },
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Exemplo de Cadastro',
                value={
                    'full_name': 'João Silva',
                    'email': 'joao.silva@email.com',
                    'password': 'securepassword123'
                }
            )
        ]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Usuário registrado com sucesso",
                    "user_key": str(user.user_id)
                }, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateOrganizationView(APIView):
    """
        Crie uma nova organização e vincule ao usuário usando a chave do usuário.
    """

    @extend_schema(
        request=OrganizationSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'organization': OrganizationSerializer().data
                }
            },
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Exemplo de Criação de Organização',
                value={
                    'name': 'Minha Empresa Ltda',
                    'email': 'contato@minhaempresa.com',
                    'organization_id': '12.345.678/0001-90',
                    'user_key': 'ABC123DEF456'
                }
            )
        ]
    )
    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save()
            return Response(
                {
                    "message": "Organização criada com sucesso",
                    "organization": OrganizationSerializer(organization).data
                }, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
        Obtenha o par de tokens JWT.
    """
    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'Endereço de email do usuário',
                        'example': 'joao.silva@email.com'
                    },
                    'password': {
                        'type': 'string',
                        'format': 'password',
                        'description': 'Senha do usuário',
                        'example': 'securepassword123'
                    }
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'refresh': {
                        'type': 'string',
                        'description': 'Token de refresh JWT',
                        'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    },
                    'access': {
                        'type': 'string',
                        'description': 'Token de acesso JWT',
                        'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            },
            401: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Exemplo de Login',
                value={
                    'email': 'joao.silva@email.com',
                    'password': 'securepassword123'
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'email' in data and 'username' not in data:
            data['username'] = data['email']
        request._full_data = data
        return super().post(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
        Altere a senha do usuário.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'current_password': {
                        'type': 'string',
                        'format': 'password',
                        'description': 'Senha atual do usuário',
                        'example': 'oldpassword123'
                    },
                    'new_password': {
                        'type': 'string',
                        'format': 'password',
                        'description': 'Nova senha para a conta',
                        'example': 'newsecurepassword123'
                    }
                },
                'required': ['current_password', 'new_password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Senha alterada com sucesso'
                    }
                }
            },
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'Exemplo de Alteração de Senha',
                value={
                    'current_password': 'oldpassword123',
                    'new_password': 'newsecurepassword123'
                }
            )
        ]
    )
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {
                    "error": "A senha atual e a nova senha são obrigatórias."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {
                    "error": "A senha atual está incorreta."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "message": "Senha alterada com sucesso"
            }, 
            status=status.HTTP_200_OK
        )
