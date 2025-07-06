from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.db.models import Q, Count, Min, Max
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import (
    User, Organization, AboutUs, Achievements, Service, Journey,
    HeroSection, PropertyType, Property, Agent, Contact
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    OrganizationSerializer, AboutUsSerializer, AchievementsSerializer,
    ServiceSerializer, JourneySerializer, HeroSectionSerializer,
    PropertyTypeSerializer, PropertySerializer, PropertyListSerializer,
    AgentSerializer, ContactSerializer, ContactCreateSerializer,
    ContactUpdateSerializer, PropertyStatsSerializer, ContactStatsSerializer,
    DashboardStatsSerializer
)


# Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)


# Organization Views
class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]


# About Us Views
class AboutUsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer
    permission_classes = [AllowAny]


# Achievements Views
class AchievementsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievements.objects.all()
    serializer_class = AchievementsSerializer
    permission_classes = [AllowAny]


# Service Views
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]


# Journey Views
class JourneyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = [AllowAny]


# Hero Section Views
class HeroSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeroSection.objects.filter(is_active=True)
    serializer_class = HeroSectionSerializer
    permission_classes = [AllowAny]


# Property Type Views
class PropertyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PropertyType.objects.filter(is_active=True)
    serializer_class = PropertyTypeSerializer
    permission_classes = [AllowAny]


# Property Views
class PropertyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_type', 'status', 'is_featured', 'bedrooms', 'bathrooms']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price', 'created_at', 'area']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        return PropertySerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured properties"""
        featured_properties = self.queryset.filter(is_featured=True, status='available')
        serializer = PropertyListSerializer(featured_properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get properties by type"""
        property_type = request.query_params.get('type')
        if property_type:
            properties = self.queryset.filter(property_type__name__icontains=property_type)
            serializer = PropertyListSerializer(properties, many=True)
            return Response(serializer.data)
        return Response({'error': 'Property type parameter is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)


# Agent Views
class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Agent.objects.filter(is_active=True)
    serializer_class = AgentSerializer
    permission_classes = [AllowAny]


# Contact Views
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'preferred_contact_method', 'assigned_agent']
    search_fields = ['first_name', 'last_name', 'email', 'subject']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContactUpdateSerializer
        return ContactSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        return Response({
            'contact': ContactSerializer(contact).data,
            'message': 'Contact submitted successfully. We will get back to you soon!'
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get contact statistics"""
        stats = {
            'total_contacts': Contact.objects.count(),
            'new_contacts': Contact.objects.filter(status='new').count(),
            'in_progress_contacts': Contact.objects.filter(status='in_progress').count(),
            'resolved_contacts': Contact.objects.filter(status='resolved').count(),
        }
        serializer = ContactStatsSerializer(stats)
        return Response(serializer.data)


# Dashboard Views
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Property stats
        property_stats = {
            'total_properties': Property.objects.count(),
            'available_properties': Property.objects.filter(status='available').count(),
            'sold_properties': Property.objects.filter(status='sold').count(),
            'pending_properties': Property.objects.filter(status='pending').count(),
            'featured_properties': Property.objects.filter(is_featured=True).count(),
        }

        # Contact stats
        contact_stats = {
            'total_contacts': Contact.objects.count(),
            'new_contacts': Contact.objects.filter(status='new').count(),
            'in_progress_contacts': Contact.objects.filter(status='in_progress').count(),
            'resolved_contacts': Contact.objects.filter(status='resolved').count(),
        }

        # General stats
        stats = {
            'property_stats': property_stats,
            'contact_stats': contact_stats,
            'total_agents': Agent.objects.filter(is_active=True).count(),
            'total_services': Service.objects.filter(is_active=True).count(),
        }

        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


# Search Views
class GlobalSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, 
                           status=status.HTTP_400_BAD_REQUEST)

        # Search properties
        properties = Property.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(location__icontains=query)
        )[:10]

        # Search agents
        agents = Agent.objects.filter(
            Q(name__icontains=query) | 
            Q(specialties__icontains=query) | 
            Q(bio__icontains=query)
        )[:5]

        # Search services
        services = Service.objects.filter(
            Q(name__icontains=query) | 
            Q(title__icontains=query) | 
            Q(features__icontains=query)
        )[:5]

        results = {
            'properties': PropertyListSerializer(properties, many=True).data,
            'agents': AgentSerializer(agents, many=True).data,
            'services': ServiceSerializer(services, many=True).data,
            'total_results': properties.count() + agents.count() + services.count()
        }

        return Response(results)


# Public API Views for Frontend
@api_view(['GET'])
@permission_classes([AllowAny])
def home_page_data(request):
    """Get all data needed for the home page"""
    try:
        # Get hero sections
        hero_sections = HeroSection.objects.filter(is_active=True)
        
        # Get featured properties
        featured_properties = Property.objects.filter(is_featured=True, status='available')[:6]
        
        # Get services
        services = Service.objects.filter(is_active=True)[:6]
        
        # Get achievements
        achievements = Achievements.objects.first()
        
        # Get organization info
        organization = Organization.objects.first()
        
        data = {
            'hero_sections': HeroSectionSerializer(hero_sections, many=True).data,
            'featured_properties': PropertyListSerializer(featured_properties, many=True).data,
            'services': ServiceSerializer(services, many=True).data,
            'achievements': AchievementsSerializer(achievements).data if achievements else None,
            'organization': OrganizationSerializer(organization).data if organization else None,
        }
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def about_page_data(request):
    """Get all data needed for the about page"""
    try:
        # Get about us info
        about_us = AboutUs.objects.first()
        
        # Get journey items
        journey_items = Journey.objects.all()
        
        # Get achievements
        achievements = Achievements.objects.first()
        
        # Get agents
        agents = Agent.objects.filter(is_active=True)
        
        data = {
            'about_us': AboutUsSerializer(about_us).data if about_us else None,
            'journey': JourneySerializer(journey_items, many=True).data,
            'achievements': AchievementsSerializer(achievements).data if achievements else None,
            'agents': AgentSerializer(agents, many=True).data,
        }
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def property_filters(request):
    """Get filter options for properties"""
    try:
        # Get property types
        property_types = PropertyType.objects.filter(is_active=True)
        
        # Get price range
        price_range = Property.objects.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Get bedroom options
        bedroom_options = Property.objects.values_list('bedrooms', flat=True).distinct().order_by('bedrooms')
        
        # Get bathroom options
        bathroom_options = Property.objects.values_list('bathrooms', flat=True).distinct().order_by('bathrooms')
        
        # Get locations
        locations = Property.objects.values_list('location', flat=True).distinct().order_by('location')
        
        data = {
            'property_types': PropertyTypeSerializer(property_types, many=True).data,
            'price_range': price_range,
            'bedroom_options': list(bedroom_options),
            'bathroom_options': list(bathroom_options),
            'locations': list(locations),
        }
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)