from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from auth.models import Membership, Organization
from .serializers import OrganizationMemberSerializer

User = get_user_model()


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar membros de uma organização.
    
    Endpoints disponíveis:
    - GET /accounts/members/ - Lista todos os membros da organização ativa
    - POST /accounts/members/ - Cria um novo membro
    - GET /accounts/members/{id}/ - Detalhe de um membro
    - PUT/PATCH /accounts/members/{id}/ - Atualiza um membro
    - DELETE /accounts/members/{id}/ - Remove um membro da organização
    """
    permission_classes = [IsAuthenticated]
    
    def get_organization(self):
        """Retorna a organização ativa do usuário logado"""
        if not hasattr(self.request.user, 'org_active') or not self.request.user.org_active:
            return None
        return self.request.user.org_active
    
    def get_queryset(self):
        """Retorna apenas usuários da organização ativa"""
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
        """Lista todos os membros da organização"""
        organization = self.get_organization()
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Cria um novo membro na organização"""
        organization = self.get_organization()
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = Membership.objects.get(
                user=request.user, 
                organization=organization
            )
            if membership.role not in [Membership.Roles.OWNER, Membership.Roles.MANAGER]:
                return Response(
                    {'detail': 'Sem permissão para adicionar membros'},
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
        """Atualiza um membro da organização"""
        organization = self.get_organization()
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance = self.get_object()
        
        try:
            membership = Membership.objects.get(
                user=request.user, 
                organization=organization
            )
            if membership.role not in [Membership.Roles.OWNER, Membership.Roles.MANAGER]:
                return Response(
                    {'detail': 'Sem permissão para atualizar membros'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Membership.DoesNotExist:
            return Response(
                {'detail': 'Usuário não é membro da organização'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Remove um membro da organização"""
        organization = self.get_organization()
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance = self.get_object()
        
        try:
            membership = Membership.objects.get(
                user=request.user, 
                organization=organization
            )
            if membership.role not in [Membership.Roles.OWNER, Membership.Roles.MANAGER]:
                return Response(
                    {'detail': 'Sem permissão para remover membros'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Membership.DoesNotExist:
            return Response(
                {'detail': 'Usuário não é membro da organização'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            target_membership = Membership.objects.get(
                user=instance, 
                organization=organization
            )
            if target_membership.role == Membership.Roles.OWNER:
                return Response(
                    {'detail': 'Não é possível remover o proprietário da organização'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Membership.DoesNotExist:
            pass
        
        Membership.objects.filter(
            user=instance, 
            organization=organization
        ).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas dos membros da organização"""
        organization = self.get_organization()
        if not organization:
            return Response(
                {'detail': 'Usuário não possui organização ativa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        memberships = Membership.objects.filter(organization=organization)
        
        stats = {
            'total_members': memberships.count(),
            'active_members': memberships.filter(is_active=True).count(),
            'inactive_members': memberships.filter(is_active=False).count(),
            'roles': {
                'owners': memberships.filter(role=Membership.Roles.OWNER).count(),
                'managers': memberships.filter(role=Membership.Roles.MANAGER).count(),
                'members': memberships.filter(role=Membership.Roles.MEMBER).count(),
            }
        }
        
        return Response(stats)
