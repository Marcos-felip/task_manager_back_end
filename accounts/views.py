from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from auth.models import Membership, Organization
from .serializers import OrganizationMemberSerializer

User = get_user_model()


class OrganizationMemberViewSet(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
    """
    ViewSet para gerenciar membros da organização ativa do usuário.
    
    Endpoints disponíveis:
    - GET /accounts/members/ - Lista membros da organização ativa do usuário
    - POST /accounts/members/ - Cria um novo membro na organização ativa do usuário
    - PUT /accounts/members/{id}/ - Atualiza completamente um membro (todos os campos)
    - PATCH /accounts/members/{id}/ - Atualiza parcialmente um membro (apenas campos enviados)
    """
    permission_classes = [IsAuthenticated]
    
    def get_organization(self):
        """Retorna a organização ativa do usuário"""
        if not hasattr(self.request.user, 'org_active') or not self.request.user.org_active:
            return None
        return self.request.user.org_active
    
    def get_queryset(self):
        """Retorna apenas usuários da organização ativa do usuário"""
        organization = self.get_organization()
        
        if not organization:
            return User.objects.none()
        
        return User.objects.filter(
            membership__organization=organization
        ).prefetch_related(
            Prefetch(
                'membership_set',
                queryset=Membership.objects.filter(organization=organization),
                to_attr='current_membership'
            )
        ).distinct()
    
    serializer_class = OrganizationMemberSerializer
    
    def get_serializer_context(self):
        """Adiciona a organização no contexto do serializer"""
        context = super().get_serializer_context()
        context['organization'] = self.get_organization()
        return context
    
    def list(self, request, *args, **kwargs):
        """Lista todos os membros da organização ativa do usuário"""
        organization = self.get_organization()
        
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = Membership.objects.get(
                user=request.user, 
                organization=organization,
                is_active=True
            )
        except Membership.DoesNotExist:
            return Response(
                {'detail': 'Usuário não é membro da organização'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Cria um novo membro na organização ativa do usuário"""
        organization = self.get_organization()
        
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = Membership.objects.get(
                user=request.user, 
                organization=organization,
                is_active=True
            )
            if membership.role not in [Membership.Roles.OWNER, Membership.Roles.MANAGER]:
                return Response(
                    {'detail': 'Sem permissão para adicionar membros. Apenas OWNER e MANAGER podem adicionar membros.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Membership.DoesNotExist:
            return Response(
                {'detail': 'Usuário não é membro da organização'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
    
    def update(self, request, *args, **kwargs):
        """Atualiza um membro da organização ativa do usuário"""
        organization = self.get_organization()
        
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = Membership.objects.get(
                user=request.user, 
                organization=organization,
                is_active=True
            )
            if membership.role not in [Membership.Roles.OWNER, Membership.Roles.MANAGER]:
                return Response(
                    {'detail': 'Sem permissão para atualizar membros. Apenas OWNER e MANAGER podem atualizar membros.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Membership.DoesNotExist:
            return Response(
                {'detail': 'Usuário não é membro da organização'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        
        if 'role' in request.data and instance == request.user:
            try:
                target_membership = Membership.objects.get(user=instance, organization=organization)
                if target_membership.role == Membership.Roles.OWNER:
                    owners_count = Membership.objects.filter(
                        organization=organization, 
                        role=Membership.Roles.OWNER,
                        is_active=True
                    ).count()
                    if owners_count <= 1:
                        return Response(
                            {'detail': 'Não é possível alterar o role do último proprietário da organização'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            except Membership.DoesNotExist:
                pass
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK, 
            headers=headers
        )
