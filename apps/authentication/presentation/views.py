from rest_framework import status, views, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from accounts.infrastructure.models.user import User
from accounts.infrastructure.models.organization import Organization
from apps.accounts.application.use_cases.create_user_with_organization_and_membership import (
    CreateUserWithOrganizationAndMembershipUseCase,
)
from accounts.infrastructure.repositories.user_repo_django import UserRepositoryDjango
from accounts.infrastructure.repositories.organization_repo_django import OrganizationRepositoryDjango
from apps.authentication.presentation.serializers import (
    RegisterSerializer,
    CreateOrgMembershipSerializer,
)


class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Registrar usuário",
        description="Cria um usuário",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="Usuário registrado", response=None),
            400: OpenApiResponse(description="Erro de validação"),
        },
        examples=[
            OpenApiExample(
                'Payload de registro',
                value={
                    "full_name": "John Doe",
                    "email": "john.doe@example.com",
                    "password": "StrongPass123!",
                },
                request_only=True,
            ),
            OpenApiExample(
                'Resposta de sucesso',
                value={
                    "email": "john.doe@example.com",
                    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3d6b56"
                },
                response_only=True,
            ),
        ],
        tags=["Auth"],
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        first_name = data.get('first_name') or ''
        last_name = data.get('last_name') or ''
        if data.get('full_name') and not (first_name or last_name):
            parts = str(data['full_name']).strip().split()
            if parts:
                first_name = parts[0]
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        obj = User.objects.create(
            email=data['email'],
            username=data.get('username'),
            first_name=first_name,
            last_name=last_name,
        )
        
        obj.set_password(data['password'])
        obj.save()

        return Response({"email": obj.email, "user_id": str(obj.user_id)}, status=status.HTTP_201_CREATED)


class CreateOrganizationMembershipView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Criar organização e vincular membership ao usuário",
        request=CreateOrgMembershipSerializer,
        responses={201: OpenApiResponse(description="Organização criada e usuário vinculado")},
    )

    def post(self, request):
        serializer = CreateOrgMembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        org_repo = OrganizationRepositoryDjango()
        user_repo = UserRepositoryDjango()

        user = user_repo.get_user_by_id(int(data['user_id']))
        if not user:
            return Response({"detail": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        org_obj = Organization.objects.create(
            name=data['organization_name'],
            email=data.get('organization_email'),
            cpf_cnpj=data['cpf_cnpj'],
        )

        use_case = CreateUserWithOrganizationAndMembershipUseCase(user_repo, org_repo)
        user_payload = {
            'user_id': user.user_id,
        }

        membership_payload = {'role': data.get('role', 'owner')}
        user, organization, membership = use_case.execute(
            user_payload,
            organization_id=int(org_obj.organization_id),
            membership_data=membership_payload,
        )

        return Response({
            "organization_id": getattr(organization, 'organization_id', None),
            "user_id": user.user_id,
            "role": membership.role,
        }, status=status.HTTP_201_CREATED)