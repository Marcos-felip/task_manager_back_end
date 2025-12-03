from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, OrganizationSerializer, CustomTokenObtainPairSerializer
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
                    'user_id': {
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
                    "user_id": str(user.user_id)
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
                    'user_id': 'ABC123DEF456'
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
    serializer_class = CustomTokenObtainPairSerializer
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
                    },
                    'user': {
                        'type': 'object',
                        'properties': {
                            'email': {
                                'type': 'string',
                                'format': 'email',
                                'description': 'Email do usuário autenticado',
                                'example': 'joao.silva@email.com'
                            },
                            'first_name': {
                                'type': 'string',
                                'description': 'Primeiro nome do usuário',
                                'example': 'João'
                            },
                            'last_name': {
                                'type': 'string',
                                'description': 'Último nome do usuário',
                                'example': 'Silva'
                            },
                            'org_active': {
                                'type': 'object',
                                'properties': {
                                    'name': {
                                        'type': 'string',
                                        'description': 'Nome da organização ativa do usuário',
                                        'example': 'Minha Empresa Ltda'
                                    },
                                    'organization_key': {
                                        'type': 'string',
                                        'description': 'Chave única da organização ativa',
                                        'example': 'ORG123KEY456'
                                    }
                                }
                            }
                        }
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