from django.contrib.auth import login, logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    User, Organization, PropertyType, Property, PropertyImage, Agent,
    PropertyInquiry, PropertyVisit, SavedProperty, Service, HeroSlide,
    JourneyStep, AboutUs, PropertyAlert
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    PropertySerializer, PropertyDetailSerializer, PropertyCreateUpdateSerializer,
    SavedPropertySerializer, SavedPropertyCreateSerializer,
    PropertyInquirySerializer, PropertyInquiryCreateSerializer,
    PropertyVisitSerializer, PropertyVisitCreateSerializer,
    AdminAnalyticsSerializer, UserManagementSerializer, UserCreateSerializer, UserUpdateSerializer,
    PropertyTypeSerializer, OrganizationSerializer, ServiceSerializer,
    AgentSerializer, HeroSlideSerializer, JourneyStepSerializer, AboutUsSerializer,
    PropertyAlertSerializer, PropertyAlertCreateSerializer
)

User = get_user_model()


# Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            logout(request)
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'message': 'User was not logged in'}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# Property Views
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateUpdateSerializer
        return PropertySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True).select_related('property_type').prefetch_related('images')
        
        # Filter parameters
        property_type = self.request.query_params.get('property_type')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        location = self.request.query_params.get('location')
        bedrooms = self.request.query_params.get('bedrooms')
        bathrooms = self.request.query_params.get('bathrooms')
        is_featured = self.request.query_params.get('is_featured')

        if property_type:
            queryset = queryset.filter(property_type_id=property_type)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if bedrooms:
            queryset = queryset.filter(bedrooms=bedrooms)
        if bathrooms:
            queryset = queryset.filter(bathrooms=bathrooms)
        if is_featured:
            queryset = queryset.filter(is_featured=True)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured properties"""
        featured_properties = self.get_queryset().filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured_properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent properties"""
        recent_properties = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_properties, many=True)
        return Response(serializer.data)


# Customer Dashboard Views
class CustomerSavedPropertiesView(generics.ListAPIView):
    serializer_class = SavedPropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedProperty.objects.filter(customer=self.request.user).select_related('property')


class CustomerSavedPropertyCreateView(generics.CreateAPIView):
    serializer_class = SavedPropertyCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if 'unique constraint' in str(e).lower():
                return Response({'message': 'Property already saved'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Error saving property'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerInquiriesView(generics.ListAPIView):
    serializer_class = PropertyInquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyInquiry.objects.filter(customer=self.request.user).select_related('property', 'agent').order_by('-created_at')


class CustomerInquiryCreateView(generics.CreateAPIView):
    serializer_class = PropertyInquiryCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CustomerVisitsView(generics.ListAPIView):
    serializer_class = PropertyVisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyVisit.objects.filter(customer=self.request.user).select_related('property', 'agent').order_by('-scheduled_date')


class CustomerVisitCreateView(generics.CreateAPIView):
    serializer_class = PropertyVisitCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# Admin Dashboard Views
class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Calculate analytics data
        total_properties = Property.objects.count()
        active_properties = Property.objects.filter(is_active=True).count()
        total_users = User.objects.count()
        total_agents = Agent.objects.count()
        total_inquiries = PropertyInquiry.objects.count()
        pending_inquiries = PropertyInquiry.objects.filter(status='pending').count()
        
        # Get scheduled visits for next 7 days
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        scheduled_visits = PropertyVisit.objects.filter(
            scheduled_date__range=[today, next_week],
            status='scheduled'
        ).count()
        
        # Get recent properties and inquiries
        recent_properties = Property.objects.filter(is_active=True).order_by('-created_at')[:5]
        recent_inquiries = PropertyInquiry.objects.select_related('customer', 'property').order_by('-created_at')[:5]
        
        analytics_data = {
            'total_properties': total_properties,
            'active_properties': active_properties,
            'total_users': total_users,
            'total_agents': total_agents,
            'total_inquiries': total_inquiries,
            'pending_inquiries': pending_inquiries,
            'scheduled_visits': scheduled_visits,
            'recent_properties': PropertySerializer(recent_properties, many=True).data,
            'recent_inquiries': PropertyInquirySerializer(recent_inquiries, many=True).data,
        }
        
        return Response(analytics_data)


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserManagementSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter parameters
        is_active = self.request.query_params.get('is_active')
        is_staff = self.request.query_params.get('is_staff')
        search = self.request.query_params.get('search')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset.order_by('-date_joined')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': 'User updated successfully'
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Don't allow deletion of superuser accounts
        if instance.is_superuser:
            return Response(
                {'message': 'Cannot delete superuser account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # Don't allow users to delete themselves
        if instance == request.user:
            return Response(
                {'message': 'Cannot delete your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(
            {'message': 'User deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle user active status"""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'message': 'Cannot deactivate your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = not user.is_active
        user.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
        })

    @action(detail=True, methods=['post'])
    def toggle_staff(self, request, pk=None):
        """Toggle user staff status"""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'message': 'Cannot modify your own staff status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_staff = not user.is_staff
        user.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': f'User staff status {"granted" if user.is_staff else "revoked"} successfully'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'recent_users': recent_users,
            'inactive_users': total_users - active_users,
        })


# Additional Views for better API functionality
class PropertyTypeListView(generics.ListAPIView):
    """Get all property types for filtering"""
    queryset = PropertyType.objects.filter(is_active=True)
    serializer_class = PropertyTypeSerializer
    permission_classes = [permissions.AllowAny]


class OrganizationDetailView(generics.RetrieveAPIView):
    """Get organization details for about page"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        return Organization.objects.first()


class ServiceListView(generics.ListAPIView):
    """Get all active services"""
    queryset = Service.objects.filter(is_active=True).order_by('order')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class HeroSlideListView(generics.ListAPIView):
    """Get all active hero slides"""
    queryset = HeroSlide.objects.filter(is_active=True).order_by('order')
    serializer_class = HeroSlideSerializer
    permission_classes = [permissions.AllowAny]


class JourneyStepListView(generics.ListAPIView):
    """Get all active journey steps"""
    queryset = JourneyStep.objects.filter(is_active=True).order_by('order')
    serializer_class = JourneyStepSerializer
    permission_classes = [permissions.AllowAny]


class AgentListView(generics.ListAPIView):
    """Get all active agents (team page)"""
    queryset = Agent.objects.filter(is_active=True)
    serializer_class = AgentSerializer
    permission_classes = [permissions.AllowAny]


class AboutUsDetailView(generics.RetrieveAPIView):
    """Get about us information"""
    queryset = AboutUs.objects.filter(is_active=True)
    serializer_class = AboutUsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        return AboutUs.objects.filter(is_active=True).first()


# Property Alert Views
class PropertyAlertListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertyAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyAlert.objects.filter(customer=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PropertyAlertCreateSerializer
        return PropertyAlertSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PropertyAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertyAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyAlert.objects.filter(customer=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {'message': 'Property alert deactivated successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )