from rest_framework import status, views, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .serializers import CreateOrgMembershipSerializer, RegisterSerializer
from apps.authentication.presentation.apis import AuthAPI

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
                    "user_name": "John Doe",
                    "user_email": "john.doe@example.com",
                    "password": "12345678"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Resposta de sucesso',
                value={
                    "user": {
                        "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3d6b56",
                        "email": "john.doe@example.com",
                        "name": "John Doe"
                    }
                },
                response_only=True,
            ),
        ],
        tags=["register"],
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user_resp = AuthAPI.register_create_user(
                user_name=data["user_name"],
                user_email=data["user_email"],
                password=data["password"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"user": user_resp["user"]}, status=status.HTTP_201_CREATED)



class CreateOrganizationMembershipView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Criar organização e vincular membro ao usuário",
        description=(
            "Cria uma nova organização, cria uma associação (membership) para o usuário informado "
            "com o papel especificado (por padrão 'manager'), e retorna os dados consolidados. "
            "Campos obrigatórios: organization_name, user_id. Campo opcional: role (default: 'manager')."
        ),
        request=CreateOrgMembershipSerializer,
        responses={
            201: OpenApiResponse(description="Organização criada e usuário vinculado", response=None),
            400: OpenApiResponse(description="Erro de validação"),
        },
        examples=[
            OpenApiExample(
                'Payload mínimo',
                value={
                    "organization_name": "Minha Organização",
                    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3d6b56"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Payload com papel explícito',
                value={
                    "organization_name": "Acme Corp",
                    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3d6b56",
                    "role": "manager"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Resposta de sucesso',
                value={
                    "organization": {
                        "id": "1f3e7c90-1234-4fcd-9a88-abcdef123456",
                        "name": "Acme Corp"
                    },
                    "membership": {
                        "id": "7a2b1c34-5678-4abc-9def-1234567890ab",
                        "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3d6b56",
                        "organization_id": "1f3e7c90-1234-4fcd-9a88-abcdef123456",
                        "role": "manager"
                    },
                    "user": {
                        "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3d6b56",
                        "email": "john.doe@example.com",
                        "name": "John Doe"
                    }
                },
                response_only=True,
            ),
        ],
        tags=["register"],
    )
    def post(self, request):
        payload = {
            "organization_name": request.data.get("organization_name"),
            "user_id": request.data.get("user_id"),
            "role": request.data.get("role", "manager"),
        }
        if not payload["organization_name"] or not payload["user_id"]:
            return Response({"detail": "organization_name e user_id são obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)

        org_resp = AuthAPI.register_create_org_membership_link_user(**payload)
        return Response(
            {
                "organization": org_resp["organization"],
                "membership": org_resp["membership"],
                "user": org_resp["user"],
            },
            status=status.HTTP_201_CREATED,
        )