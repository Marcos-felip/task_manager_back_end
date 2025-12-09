from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from apps.accounts.application.use_cases.create_user_with_organization_and_membership import (
    CreateUserWithOrganizationAndMembershipUseCase,
)
from accounts.presentation.serializers.user_serializer import (
    UserSerializer,
    CreateUserMembershipInputSerializer,
)

from accounts.infrastructure.repositories.user_repo_django import UserRepositoryDjango
from accounts.infrastructure.repositories.organization_repo_django import OrganizationRepositoryDjango


class UserViewSet(viewsets.ViewSet):
    @extend_schema(
        summary="Listar usuários",
        responses={200: OpenApiResponse(response=UserSerializer, description="Lista de usuários")},
    )
    def list(self, request):
        try:
            user_repo = UserRepositoryDjango()
            users = []
            for user_obj in user_repo.get_all_users():
                serializer = UserSerializer(instance=user_obj)
                users.append(serializer.data)

            return Response(users, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
    @extend_schema(
        summary="Obter usuário por ID",
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Usuário encontrado"),
            404: OpenApiResponse(description="Usuário não encontrado"),
        },
        examples=[
            OpenApiExample('Exemplo de ID', value={"pk": 1}, request_only=True),
        ],
    )
    def retrieve(self, request, pk=None):
        try:
            user_repo = UserRepositoryDjango()
            user = user_repo.get_user_by_id(int(pk))
            if not user:
                return Response(
                    {
                        "detail": "Usuário não encontrado."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    @extend_schema(
        summary="Criar usuário e vincular à organização",
        description="Cria um usuário, vincula como ativo a uma organização e registra o vínculo (membership).",
        request=CreateUserMembershipInputSerializer,
        responses={
            201: OpenApiResponse(response=UserSerializer, description="Usuário criado"),
            400: OpenApiResponse(description="Erro de validação"),
        },
        examples=[
            OpenApiExample(
                'Exemplo de criação',
                value={
                    "user": {
                        "email": "john.doe@example.com",
                        "username": "john",
                    },
                    "organization_id": "c6a9f1a4-3f7d-4e4a-9b2b-2e9d1e9a1234",
                    "membership": {
                        "role": "member"
                    }
                },
            )
        ],
    )
    def create(self, request):
        try:
            # Validação via serializer de entrada para documentar e validar swagger
            input_serializer = CreateUserMembershipInputSerializer(data=request.data)
            input_serializer.is_valid(raise_exception=True)
            validated = input_serializer.validated_data

            user_data = validated.get('user') or {}
            organization_id = validated.get('organization_id')
            membership_data = validated.get('membership') or {}

            if not organization_id:
                return Response(
                    {
                        "detail": "'organization_id' é obrigatório"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_repo = UserRepositoryDjango()
            org_repo = OrganizationRepositoryDjango()

            use_case = CreateUserWithOrganizationAndMembershipUseCase( user_repo, org_repo)
            user, organization, membership = use_case.execute( user_data, organization_id, membership_data)

            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
    @extend_schema(
        summary="Atualizar usuário e vínculo",
        request=CreateUserMembershipInputSerializer,
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Usuário atualizado"),
            400: OpenApiResponse(description="Erro de validação"),
        },
    )
    def update(self, request, pk=None):
        try:
            user_data = request.data.get('user') or {}
            organization_id = request.data.get('organization_id')
            membership_data = request.data.get('membership') or {}

            if not organization_id:
                return Response(
                    {
                        "detail": "'organization_id' é obrigatório"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_repo = UserRepositoryDjango()
            org_repo = OrganizationRepositoryDjango()

            use_case = CreateUserWithOrganizationAndMembershipUseCase( user_repo, org_repo)
            user, organization, membership = use_case.execute( user_data, organization_id, membership_data)

            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
    @extend_schema(
        summary="Excluir usuário",
        responses={204: OpenApiResponse(description="Excluído com sucesso"), 404: OpenApiResponse(description="Usuário não encontrado")},
    )
    def destroy(self, request, pk=None):
        try:
            user_repo = UserRepositoryDjango()
            user = user_repo.get_user_by_id(int(pk))
            if not user:
                return Response(
                    {
                        "detail": "Usuário não encontrado."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            user_repo.delete_user(int(pk))
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
